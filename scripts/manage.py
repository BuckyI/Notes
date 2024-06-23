from datetime import datetime
from pathlib import Path

import streamlit as st
from datatype import HTML
from pandas import DataFrame


@st.cache_data
def load_file(filename: str):
    path = Path(__file__).parent.parent / "html" / filename
    return open(path, encoding="utf-8").read()


source = Path(__file__).parent.parent / "html"
files = DataFrame([HTML.from_file(i) for i in source.rglob("*.html")])

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
    if overwrite and (files["title"] == html.title).any():  # overwrite existed old file
        old_filename: str = files[files["title"] == html.title]["filename"].values[0]
        uploaded_file.name = old_filename
        st.warning(f"overwrite `{old_filename}` since they have same title: `{html.title}`.")

    info.info(f"saving to `{uploaded_file.name}`, confirm?")
    if st.button("confirm"):
        path = source / uploaded_file.name
        path.write_bytes(uploaded_file.getvalue())
        info.info(f"saved to `{path}`")


# reload
st.divider()
if st.button("reload"):
    st.rerun()
