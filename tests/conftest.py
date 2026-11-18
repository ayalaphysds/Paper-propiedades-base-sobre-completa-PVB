"""Pytest configuration for V6 E2E test markers without impacting legacy suites."""


def pytest_configure(config):
    """Register tier1-tier5 markers so pytest -m tierN runs with zero warnings."""
    config.addinivalue_line("markers", "tier1: Tier 1 Feature Coverage tests (60 tests)")
    config.addinivalue_line("markers", "tier2: Tier 2 Boundary, Corner & Regression Guard tests (60 tests)")
    config.addinivalue_line("markers", "tier3: Tier 3 Cross-Feature Combination tests (10 tests)")
    config.addinivalue_line("markers", "tier4: Tier 4 Real-World End-to-End Acceptance Scenarios (6 tests)")
    config.addinivalue_line("markers", "tier5: Tier 5 White-Box Adversarial Hardening tests")
