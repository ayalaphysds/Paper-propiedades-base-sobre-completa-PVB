"""
Master E2E Test Runner for Overcomplete Perfect Vortex Beams (PVB) Project.
Executes and aggregates all 4 test tiers:
- Tier 1: Core Feature Coverage (>=5 tests per feature group)
- Tier 2: Boundary, Corner & Limit Stress Cases (>=5 tests per category)
- Tier 3: Cross-Feature Pairwise Consistency
- Tier 4: Real-World Workloads & Packaging

Lead Author: Sebastián Ayala (Cauquenes, Chile)
E2E Test Architecture: e2e_tester_1
"""

import argparse
import sys
import time
import unittest
from io import StringIO
from pathlib import Path

# Add project root to sys.path so tests can import modules directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import all test suites
from tests.test_tier1_feature_coverage import (
    TestAuthorMetadata,
    TestAIEthicsDeclaration,
    TestEducationalAppendices,
    TestExactInnerProductAndBessel,
    TestContinuousFrameBounds,
    TestPhysicalUnfeasibilityProofs,
    TestSimulationScriptsAndFigures,
    TestCompilationAndOverleafPackaging,
    TestPageCountEnforcement,
)
from tests.test_tier2_boundary_corner_cases import (
    TestSingularLimitW0,
    TestLargeRadiusThinRingRegime,
    TestHighTopologicalCharge,
    TestEmptyAndMalformedInputs,
    TestFileCorruptionAndResilience,
)
from tests.test_tier3_cross_feature_combinations import (
    TestCrossFeatureConsistency,
)
from tests.test_tier4_real_world_scenarios import (
    TestRealWorldScenarios,
)


TIER_MAPPING = {
    1: [
        TestAuthorMetadata,
        TestAIEthicsDeclaration,
        TestEducationalAppendices,
        TestExactInnerProductAndBessel,
        TestContinuousFrameBounds,
        TestPhysicalUnfeasibilityProofs,
        TestSimulationScriptsAndFigures,
        TestCompilationAndOverleafPackaging,
        TestPageCountEnforcement,
    ],
    2: [
        TestSingularLimitW0,
        TestLargeRadiusThinRingRegime,
        TestHighTopologicalCharge,
        TestEmptyAndMalformedInputs,
        TestFileCorruptionAndResilience,
    ],
    3: [
        TestCrossFeatureConsistency,
    ],
    4: [
        TestRealWorldScenarios,
    ],
}


def build_suite(tier: int = None) -> unittest.TestSuite:
    """Build a test suite for a specific tier or all tiers."""
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()

    tiers_to_load = [tier] if tier in TIER_MAPPING else [1, 2, 3, 4]

    for t in tiers_to_load:
        for test_class in TIER_MAPPING[t]:
            suite.addTests(loader.loadTestsFromTestCase(test_class))

    return suite


class CustomTestResult(unittest.TextTestResult):
    """Custom test result recorder with tier-aware metrics."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0

    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1


def run_e2e_tests(tier: int = None, verbosity: int = 2) -> bool:
    """Run E2E tests and print formatted dashboard summary."""
    print("=" * 80)
    print("      E2E TEST HARNESS: OVERCOMPLETE PERFECT VORTEX BEAMS (PVB)")
    print("      Author: Sebastián Ayala | E2E Testing Track (e2e_tester_1)")
    print("=" * 80)

    start_time = time.time()
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    total_run = 0

    tiers = [tier] if tier in TIER_MAPPING else [1, 2, 3, 4]
    tier_results = {}

    for t in tiers:
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        for test_class in TIER_MAPPING[t]:
            suite.addTests(loader.loadTestsFromTestCase(test_class))

        stream = StringIO()
        runner = unittest.TextTestRunner(stream=stream, resultclass=CustomTestResult, verbosity=verbosity)
        result = runner.run(suite)

        t_run = result.testsRun
        t_passed = result.success_count
        t_failed = len(result.failures) + len(result.errors)
        t_skipped = len(result.skipped)

        tier_results[t] = {
            "run": t_run,
            "passed": t_passed,
            "failed": t_failed,
            "skipped": t_skipped,
            "failures": result.failures + result.errors,
            "skipped_details": result.skipped,
        }

        total_run += t_run
        total_passed += t_passed
        total_failed += t_failed
        total_skipped += t_skipped

    elapsed_time = time.time() - start_time

    # Print Dashboard Table
    print("\n+-----------------------------------------------------------------------------+")
    print("| Tier  | Description                   | Total | Passed | Pending/Skip | Fail |")
    print("+-------+-------------------------------+-------+--------+--------------+------+")
    tier_labels = {
        1: "Tier 1: Feature Coverage       ",
        2: "Tier 2: Boundary & Corner Limit ",
        3: "Tier 3: Cross-Feature Consist.  ",
        4: "Tier 4: Real-World Workloads    ",
    }
    for t in tiers:
        res = tier_results[t]
        label = tier_labels.get(t, f"Tier {t}                         ")
        print(f"| T{t}   | {label} | {res['run']:5d} | {res['passed']:6d} | {res['skipped']:12d} | {res['failed']:4d} |")
    print("+-------+-------------------------------+-------+--------+--------------+------+")
    print(f"| TOTAL | All Verification Tiers        | {total_run:5d} | {total_passed:6d} | {total_skipped:12d} | {total_failed:4d} |")
    print("+-----------------------------------------------------------------------------+")
    print(f"Total Execution Time: {elapsed_time:.3f} seconds\n")

    # Pending deliverables note
    if total_skipped > 0:
        print("[*] NOTICE: Pending deliverables detected (normal progressive testability state):")
        for t in tiers:
            for test, reason in tier_results[t]["skipped_details"]:
                print(f"    - [{test.id().split('.')[-1]}] {reason}")
        print("    These tests will automatically pass once corresponding Milestone workers deliver the files.\n")

    # Failures note
    if total_failed > 0:
        print("[!] REGRESSIONS DETECTED:")
        for t in tiers:
            for test, err in tier_results[t]["failures"]:
                print(f"    - FAIL: {test.id()}")
                print(f"      Error: {err.splitlines()[-1]}")
        print("\nResult: FAILED\n")
        return False
    else:
        print("[+] All active tests PASSED with zero failures and zero regressions.")
        print("Result: SUCCESS\n")
        return True


def main():
    parser = argparse.ArgumentParser(description="Master E2E Test Runner for PVB Project")
    parser.add_argument("--tier", "-t", type=int, choices=[1, 2, 3, 4], default=None,
                        help="Execute only a specific test tier (1, 2, 3, or 4)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose test output")
    args = parser.parse_args()

    verbosity = 2 if args.verbose else 1
    success = run_e2e_tests(tier=args.tier, verbosity=verbosity)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
