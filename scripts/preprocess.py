import re
from pathlib import Path
from typing import NamedTuple

import yaml


class HTML(NamedTuple):
    title: str
    url: str
    path: Path

    _title_pattern = re.compile("<title>(.*)</title>")
    _url_pattern = re.compile("^ url: (.*) $", re.MULTILINE)  # SingleFile added

    @classmethod
    def from_file(cls, path: Path) -> "HTML":
        text = open(path, encoding="utf-8").read()
        title = "Untitled"
        url = ""
        if match := cls._title_pattern.search(text):
            title = match.group(1)
        if match := cls._url_pattern.search(text):
            url = match.group(1)
        return cls(title=title, url=url, path=path)

    def markdown_link(self) -> str:
        return f"[{self.title}]({self.url})" if self.url else self.title

    @property
    def truncated_title(self, max_len: int = 20) -> str:
        if len(self.title) > max_len:
            return self.title[:max_len] + "..."
        return self.title


work_dir = Path(__file__).parent.parent
data = yaml.safe_load(open(work_dir / "mkdocs.yml"))

docs_dir = work_dir / "docs"
html_dir = docs_dir / "html"
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

    web_notes.extend({i.truncated_title: i.path.relative_to(docs_dir).as_posix()} for i in htmls)

    # update mkdocs.yml
    data["nav"] = data.get("nav", [])
    data["nav"].append({"Web Notes": web_notes})

# save
with open(work_dir / "mkdocs_mod.yml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True)
