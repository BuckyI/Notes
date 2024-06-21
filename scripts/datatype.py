import re
from pathlib import Path
from typing import NamedTuple


class HTML(NamedTuple):
    title: str
    url: str
    filename: str

    _title_pattern = re.compile("<title>(.*)</title>")
    _url_pattern = re.compile("^ url: (.*) $", re.MULTILINE)  # SingleFile added

    @classmethod
    def from_text(cls, text: str, filename: str = "") -> "HTML":
        title = "Untitled"
        url = ""
        if match := cls._title_pattern.search(text):
            title = match.group(1)
        if match := cls._url_pattern.search(text):
            url = match.group(1)
        return cls(title=title, url=url, filename=filename)

    @classmethod
    def from_file(cls, path: Path) -> "HTML":
        text = open(path, encoding="utf-8").read()
        return cls.from_text(text, path.name)

    def markdown_link(self) -> str:
        return f"[{self.title}]({self.url})" if self.url else self.title

    @property
    def truncated_title(self, max_len: int = 20) -> str:
        if len(self.title) > max_len:
            return self.title[:max_len] + "..."
        return self.title
