import requests
import json
from pathlib import Path

API_URL = "http://localhost:8000"

def test_endpoint(name, method, endpoint, payload=None):
    print(f"Testing {name} [{method} {endpoint}]...")
    try:
        if method == "GET":
            r = requests.get(f"{API_URL}{endpoint}")
        else:
            r = requests.post(f"{API_URL}{endpoint}", json=payload)
        
        if r.status_code == 200:
            print(f"  [SUCCESS] {name}")
            return r.json()
        else:
            print(f"  [FAIL] {name} - Status {r.status_code}: {r.text}")
            return None
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return None

def main():
    print("--- EVOPYRAMID E2E API AUDIT ---")
    
    # 1. Sessions
    test_endpoint("Session List", "GET", "/v1/sessions")
    test_endpoint("Providers", "GET", "/v1/providers")
    
    # 2. Workspace Tree
    tree = test_endpoint("Workspace Tree", "GET", "/v1/workspace/tree")
    if tree:
        print(f"  Project Root: {tree.get('name')}")
    
    # 3. Workspace Read
    test_endpoint("Read init file", "GET", "/v1/workspace/file?path=beta_pyramid_functional/__init__.py")
    
    # 4. Staging & Commit Cycle
    test_path = "tmp/e2e_test_file.txt"
    staged = test_endpoint("Stage File Write", "POST", "/v1/workspace/file", {
        "path": test_path,
        "content": "E2E Test Success",
        "overwrite": True
    })
    
    if staged:
        test_endpoint("Commit File Write", "POST", "/v1/workspace/commit", {
            "path": test_path,
            "content": "E2E Test Success - Final",
            "overwrite": True
        })
        
        # Cleanup check
        full_path = Path(__file__).parent / test_path
        if full_path.exists():
             print(f"  [DISK] File verified at {test_path}")
        else:
             print(f"  [DISK] File NOT found at {test_path}")

if __name__ == "__main__":
    main()
