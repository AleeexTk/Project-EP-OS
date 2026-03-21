import os
from pathlib import Path

def find_empty_py_files(directory):
    empty_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = Path(root) / file
                if path.stat().st_size == 0 and not file.startswith('__'):
                    empty_files.append(str(path))
    return empty_files

if __name__ == '__main__':
    project_root = Path(__file__).resolve().parent
    empty_nodes = find_empty_py_files(project_root)
    print(f"Found {len(empty_nodes)} empty Python files (0 bytes):")
    for doc in empty_nodes:
        print(f" - {Path(doc).relative_to(project_root)}")
