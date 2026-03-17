import os
from pathlib import Path

def fill_empties():
    root = Path(r"c:\Users\Alex Bear\Desktop\EvoPyramid OS\beta_pyramid_functional")
    count = 0
    for p in root.rglob("*.py"):
        if p.stat().st_size == 0 and not p.name.startswith("__"):
            name = p.stem.replace("_", " ").title()
            content = f'"""\n{name} Module\nThis is a structural placeholder awaiting functional implementation.\n"""\n\nimport logging\n\nlogger = logging.getLogger(__name__)\n\ndef initialize():\n    logger.debug(f"{name} initialized.")\n    pass\n'
            p.write_text(content, encoding='utf-8')
            count += 1
            print(f"Filled: {p.relative_to(root)}")
    print(f"\nSuccessfully filled {count} empty .py files with valid boilerplate.")
            
if __name__ == "__main__":
    fill_empties()
