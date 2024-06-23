from datetime import datetime
from pathlib import Path

import streamlit as st
from datatype import HTML
from git import Repo
from pandas import DataFrame

WORKDIR = Path(__file__).parent.parent
HTMLDIR = WORKDIR / "html"


@st.cache_data
def load_file(filename: str):
    path = HTMLDIR / filename
    return open(path, encoding="utf-8").read()


def commit_and_push():
    "upload new notes to github, use with caution"
    repo = Repo(WORKDIR)
    modified = [d.a_path for d in repo.index.diff(None) if d.a_path.startswith("html")]
    added = [f for f in repo.untracked_files if f.startswith("html")]
    changed = 0
    if modified:
        res = repo.index.add(modified)
        changed += len(res)
        repo.index.commit(f"Update {len(modified)} " + "note" if len(added) == 1 else "notes")
    if added:
        res = repo.index.add(added)
        changed += len(res)
        repo.index.commit(f"Add {len(added)} " + "note" if len(added) == 1 else "notes")

    remote = repo.remote()
    remote.pull()
    remote.push().raise_if_error()
    return changed


files = DataFrame([HTML.from_file(i) for i in HTMLDIR.rglob("*.html")])

files["_selected"] = False  # select to download!
edited_files = st.data_editor(
    files,
    column_order=["title", "_selected", "url"],
    column_config={
        "title": st.column_config.TextColumn(disabled=True),
        "_selected": "📥",  # only this column can be modified
        "url": st.column_config.LinkColumn("🔗", disabled=True),
    },
    hide_index=True,
)
if edited_files["_selected"].any():
    with st.popover("download selected html files"):
        for idx, f in edited_files[edited_files["_selected"]].iterrows():
            st.download_button(f["title"], data=load_file(f["filename"]), file_name=f["filename"])


# upload html file
uploaded_file = st.file_uploader("upload html file", type="html")
overwrite = st.checkbox("overwrite same title")
info = st.empty()
if uploaded_file is not None:
    uploaded_file.name = datetime.now().strftime("%Y%m%d%H%M%S") + ".html"
    html = HTML.from_text(uploaded_file.read().decode("utf-8"), uploaded_file.name)
    if (files["title"] == html.title).any():
        info.warning(f"File with title '`{html.title}`' already exists.")
        if overwrite:  # overwrite existed old file
            old_filename: str = files[files["title"] == html.title]["filename"].values[0]
            uploaded_file.name = old_filename
            info.warning(f"Overwrite '**`{old_filename}`**' since it has title '`{html.title}`'.")

    if st.button("confirm"):
        path = HTMLDIR / uploaded_file.name
        path.write_bytes(uploaded_file.getvalue())
        info.info(f"saved to `{path}`")

if st.button("update github"):
    res = commit_and_push()
    info.info(f"{res} notes updated/added.")

# reload
st.divider()
if st.button("reload"):
    st.rerun()
