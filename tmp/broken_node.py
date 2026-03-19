# BROKEN NODE FOR V9.0 SELF-HEALING TEST
# This node will fail because it tries to import a non-existent module
# or uses a wrong path for core modules.

try:
    from non_existent_package.module import Something
except ImportError as e:
    print(f"[AUTORUN FAILED] Traceback (most recent call last):")
    print(f"  File \"{__file__}\", line 7, in <module>")
    print(f"    from non_existent_package.module import Something")
    print(f"ModuleNotFoundError: No module named 'non_existent_package'")
    raise e
