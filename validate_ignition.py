import httpx
import asyncio
import sys
import os
from pathlib import Path

# --- CONFIG ---
API_CORE = "http://127.0.0.1:8000"
API_SESSION = "http://127.0.0.1:8001"
ROOT_DIR = Path(__file__).resolve().parents[0]

class EvoValidator:
    def __init__(self):
        self.results = []

    def log(self, name, success, message=""):
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append(f"{status} | {name}: {message}")
        print(f"{status} | {name}: {message}")

    async def check_api_health(self, url, name):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{url}/health")
                if resp.status_code == 200:
                    self.log(f"API {name}", True, f"Online ({resp.json().get('status', 'ok')})")
                else:
                    self.log(f"API {name}", False, f"Status code {resp.status_code}")
        except Exception as e:
            self.log(f"API {name}", False, str(e))

    async def check_architectural_audit(self):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{API_CORE}/health/audit")
                if resp.status_code == 200:
                    data = resp.json()
                    status = data.get("status")
                    issues = data.get("issues", [])
                    self.log("Reality Audit", status == "HEALTHY", f"Status: {status}, Issues: {len(issues)}")
                    for issue in issues:
                        print(f"   -> [ISSUE] {issue}")
                else:
                    self.log("Reality Audit", False, f"HTTP {resp.status_code}")
        except Exception as e:
            self.log("Reality Audit", False, str(e))

    def check_local_integrity(self):
        # 1. State file
        state_file = ROOT_DIR / "state" / "pyramid_state.json"
        self.log("State File Existence", state_file.exists(), str(state_file))
        
        # 2. Key Directories
        layers = ["alpha_pyramid_core", "beta_pyramid_functional", "gamma_pyramid_reflective"]
        for l in layers:
            path = ROOT_DIR / l
            self.log(f"Layer Check: {l}", path.exists(), "Found" if path.exists() else "MISSING")

    async def run_all(self):
        print("\n" + "="*50)
        print("      EVOPYRAMID OS: VALIDATION SUITE      ")
        print("="*50 + "\n")
        
        self.check_local_integrity()
        await self.check_api_health(API_CORE, "Core Engine (:8000)")
        await self.check_api_health(API_SESSION, "Session Registry (:8001)")
        await self.check_architectural_audit()
        
        print("\n" + "="*50)
        print("      VALIDATION SUMMARY      ")
        print("="*50)
        passes = sum(1 for r in self.results if "✅ PASS" in r)
        fails = len(self.results) - passes
        print(f"TOTAL: {len(self.results)} | PASS: {passes} | FAIL: {fails}")
        if fails > 0:
            sys.exit(1)

if __name__ == "__main__":
    validator = EvoValidator()
    asyncio.run(validator.run_all())
