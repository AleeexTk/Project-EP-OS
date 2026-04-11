from beta_pyramid_functional.B2_Orchestrator.zbus import ZBus, zbus


def test_zbus_bridge_importable() -> None:
    assert ZBus is not None
    assert zbus is not None


def test_evo_api_importable_and_has_kernel_dispatch_route() -> None:
    from beta_pyramid_functional.D_Interface.evo_api import app

    paths = {getattr(route, "path", "") for route in app.routes}
    assert "/kernel/dispatch" in paths


def test_trinity_resonance_bootstrap_available() -> None:
    from alpha_pyramid_core.SPINE._17_GLOBAL_NEXUS.nexus_core import Z17GlobalNexus

    assert Z17GlobalNexus.RESONANCE is not None

