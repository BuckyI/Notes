import re
import shutil
from pathlib import Path

import yaml
from datatype import HTML

work_dir = Path(__file__).parent.parent
data = yaml.safe_load(open(work_dir / "mkdocs.yml"))

docs_dir = work_dir / "docs"
html_dir = docs_dir / "html"
if html_dir.exists():
    shutil.rmtree(html_dir)
shutil.copytree(work_dir / "html", html_dir)
# search html files
htmls = [HTML.from_file(i) for i in html_dir.rglob("*.html")]
if htmls:
    web_notes = []
    # update index
    index = Path(html_dir, "index.md")
    if index.exists():  # add index
        web_notes.append(index.relative_to(docs_dir).as_posix())
        with open(index, encoding="utf-8", mode="a") as f:
            f.write("\n\n")  # make sure there is a blank line
            f.writelines([f"- {i.markdown_link()}\n" for i in htmls])

    web_notes.extend({i.title: Path(html_dir, i.filename).relative_to(docs_dir).as_posix()} for i in htmls)

    # update mkdocs.yml
    data["nav"] = data.get("nav", [])
    data["nav"].append({"Web Notes": web_notes})

# save
with open(work_dir / "mkdocs_mod.yml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True)
