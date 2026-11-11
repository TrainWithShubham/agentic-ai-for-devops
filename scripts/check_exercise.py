"""Check a learner exercise or the supplied solution."""

import argparse
import importlib.util
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exercise", choices=["health"])
    parser.add_argument("--solution", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    path = root / ("solutions" if args.solution else "exercises") / "health_tool.py"
    spec = importlib.util.spec_from_file_location("health_exercise", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sample = {"service": "checkout", "status": "unhealthy", "http_status": 503}
    try:
        answer = module.health_summary(sample)
        assert "checkout" in answer and "503" in answer and "unhealthy" in answer
        for invalid in ({"service": "billing"}, {"service": "checkout", "status": "healthy"}):
            try:
                module.health_summary(invalid)
                raise AssertionError("Invalid input was accepted")
            except ValueError:
                pass
    except NotImplementedError:
        print(
            "Exercise not implemented yet. Edit exercises/health_tool.py; --solution checks the completed version."
        )
        return 1
    print("Health exercise passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
