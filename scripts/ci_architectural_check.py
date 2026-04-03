import os
import sys
import json
import re
import subprocess
from pathlib import Path

# Ensure UTF-8 output for Windows terminals
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', errors='replace')

def extract_keywords(text: str) -> set[str]:
    """Extract significant keywords from a string, ignoring common filler words."""
    # Simple list of stop words to filter out
    stop_words = {"and", "the", "for", "with", "from", "into", "point", "layer", "entry"}
    # Find all words, lowercase them, and filter
    words = re.findall(r'\w+', text.lower())
    return {w for w in words if len(w) > 3 and w not in stop_words}

def main():
    print("Running Smart Architectural Deduplication Check...")
    project_root = Path(os.environ.get("GITHUB_WORKSPACE", Path(__file__).resolve().parents[1]))
    
    arch_map_path = project_root / "architecture" / "architecture_map.json"
    sol_cat_path = project_root / "architecture" / "solution_catalog.json"
    
    if not arch_map_path.exists():
        print("Error: architecture/architecture_map.json not found.")
        sys.exit(1)

    with open(arch_map_path, "r", encoding="utf-8") as f:
        arch_map = json.load(f)
    
    sol_cat = {}
    if sol_cat_path.exists():
        with open(sol_cat_path, "r", encoding="utf-8") as f:
            sol_cat = json.load(f)

    # Dictionary of module_id -> set of keywords from its role
    module_roles = {
        m_id: extract_keywords(m_info.get("role", ""))
        for m_id, m_info in arch_map.get("modules", {}).items()
    }
    
    # Set of current known module names for filename matching
    known_modules = [m.lower() for m in arch_map.get("modules", {}).keys()]
    
    # Get changed files from git
    try:
        # Defaulting to comparing main...HEAD or similar. 
        # In CI, origin/main is usually the target.
        base_ref = os.environ.get("GITHUB_BASE_REF", "origin/main")
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_ref}...HEAD"], 
            capture_output=True, text=True
        )
        if result.returncode != 0:
            # Fallback if origin/main doesn't exist locally or refs are weird
            result = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True)
            
        changed_files = result.stdout.strip().split('\n')
    except Exception as e:
        print(f"Warning: Could not run git diff. Skipping file scan. ({e})")
        changed_files = []

    issues_found = 0

    for file_path_str in changed_files:
        if not file_path_str or not file_path_str.endswith(".py"):
            continue
        
        file_path = project_root / file_path_str
        if not file_path.exists():
            continue
            
        file_name_stem = file_path.stem.lower()
        print(f"Analyzing: {file_path_str}")

        # Layer 1: Filename Overlap
        for mod in known_modules:
            if file_name_stem in mod or mod.startswith(file_name_stem):
                print(f"::warning file={file_path_str}::[Layer 1] Filename '{file_path_str}' suspiciously resembles existing module '{mod}'.")
                issues_found += 1

        # Layer 2: Role/Content Overlap
        try:
            content = file_path.read_text(encoding="utf-8")
            # Extract keywords from the first 50 lines (usually docstrings/imports/main classes)
            sample_text = "\n".join(content.splitlines()[:50])
            file_keywords = extract_keywords(sample_text)
            
            for m_id, m_keywords in module_roles.items():
                overlap = file_keywords.intersection(m_keywords)
                if len(overlap) >= 2:
                    overlap_str = ", ".join(overlap)
                    print(f"::warning file={file_path_str}::[Layer 2] Possible functional duplication! File matches keywords of '{m_id}' role: {{ {overlap_str} }}.")
                    issues_found += 1
        except Exception as e:
            print(f"Could not read {file_path_str}: {e}")

    # Layer 3: Solution Intent Matching (General check on all solutions)
    # This is more global. If a new file looks like it's trying to be a 'dispatcher' or 'orchestrator'
    # we should check if those solutions are already cataloged.
    # (Simplified for now - can be expanded)

    if issues_found == 0:
        print("No obvious architectural duplicates found.")
    else:
        print(f"Warning: Architectural Check found {issues_found} potential duplication issues.")

    print("Smart Check Complete.")

if __name__ == "__main__":
    main()
