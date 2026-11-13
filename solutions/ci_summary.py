"""One possible implementation of the CI summary exercise."""


def ci_summary(run):
    if not isinstance(run, dict) or type(run.get("run_id")) is not int or run["run_id"] != 1042:
        raise ValueError("Only synthetic run 1042 is supported")
    if (
        run.get("conclusion") not in ("failure", "success")
        or not isinstance(run.get("failed_step"), str)
        or not run["failed_step"].strip()
    ):
        raise ValueError("Missing or invalid conclusion/step")
    return f"Run 1042: {run['conclusion']} at {run['failed_step']}"
