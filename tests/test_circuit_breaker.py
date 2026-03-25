import sys
import os
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(PROJECT_ROOT))

# Add required paths for imports
sys.path.append(str(Path("beta_pyramid_functional/B3_SessionRegistry")))
sys.path.append(str(Path("beta_pyramid_functional/B2_ProviderMatrix")))

from session_models import Provider
from provider_matrix import ProviderMatrix
import time

class TestCircuitBreaker(unittest.TestCase):
    def test_provider_fallback(self):
        print("\n[TEST] Circuit Breaker: Testing Z15 Provider Selection")
        
        best_provider = ProviderMatrix.get_best_available(z_level=15, sector="core")
        print(f"Original Best Provider for Z15: {best_provider.value}")
        self.assertEqual(best_provider, Provider.GEMINI)
        
        print(f"[TEST] Simulating failure on {best_provider.value} (60s cooldown)...")
        ProviderMatrix.mark_failed(best_provider, cooldown_seconds=60)
        self.assertFalse(ProviderMatrix.is_available(best_provider))
        
        fallback_provider = ProviderMatrix.get_best_available(z_level=15, sector="core")
        print(f"Fallback Provider Selected: {fallback_provider.value}")
        self.assertNotEqual(fallback_provider, best_provider)
        self.assertEqual(fallback_provider, Provider.CLAUDE) 
        
        print("[TEST] SUCCESS: System successfully isolated the failing provider and switched to the backup.")

if __name__ == "__main__":
    unittest.main()
