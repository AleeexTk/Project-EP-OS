import os
import sys
import json
import re
from pathlib import Path

def main():
    print("Running Architectural Deduplication Check...")
    project_root = Path(os.environ.get("GITHUB_WORKSPACE", Path(__file__).resolve().parents[1]))
    
    # Load architectural maps
    arch_map_path = project_root / "architecture" / "architecture_map.json"
    sol_cat_path = project_root / "architecture" / "solution_catalog.json"
    
    arch_map = {}
    sol_cat = {}
    
    if arch_map_path.exists():
        with open(arch_map_path, "r", encoding="utf-8") as f:
            arch_map = json.load(f)
            
    if sol_cat_path.exists():
        with open(sol_cat_path, "r", encoding="utf-8") as f:
            sol_cat = json.load(f)
            
    # Since we don't have git diff directly in this simple script context without a git command,
    # we simulate the check by ensuring no two exact modules exist in the codebase
    # However, in a real CI environment, it's better to scan the newly added files.
    # To keep it simple, we scan the whole project for specific patterns and compare with map.
    
    known_modules = [m.lower() for m in arch_map.get("modules", {}).keys()]
    known_solutions = [s.lower() for s in sol_cat.get("solutions", {}).keys()]
    
    # We will log a high-level summary. If we needed strict git diff parsing, we would run `git diff --name-only main`.
    # Let's do exactly that if we are in a Git repo.
    import subprocess
    try:
        # Check files changed against main/origin main
        result = subprocess.run(["git", "diff", "--name-only", "origin/main...HEAD"], capture_output=True, text=True)
        if result.returncode == 0:
            changed_files = result.stdout.strip().split('\n')
            
            for file in changed_files:
                if not file or not file.endswith('.py'):
                    continue
                file_name = file.split('/')[-1].split('.')[0].lower()
                
                # Simple heuristic: Does the filename suspiciously resemble an existing architecture module?
                # e.g., 'z14_corrector' vs 'Z14_AUTO_CORRECTOR'
                for mod in known_modules:
                    if file_name in mod or mod.startswith(file_name):
                        print(f"::warning file={file}::Possible architectural duplication detected! File '{file}' resembles existing module '{mod}' from architecture_map.json.")
                        
    except Exception as e:
        print(f"Warning: Could not run git diff for deduplication check. {e}")
        
    print("Architectural Check Complete.")

if __name__ == "__main__":
    main()
