import shutil
from pathlib import Path

work_dir = Path(__file__).parent.parent
dirs = [work_dir / "docs/html", work_dir / "mkdocs_mod.yml"]
for d in dirs:
    if d.is_file():
        d.unlink()
    if d.is_dir():
        shutil.rmtree(d)
