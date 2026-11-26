"""Export a portable dashboard from the same data used by the pipeline."""

import json
import os
from importlib.resources import files
from pathlib import Path


def write_dashboard(path, pharma, supplements, forecasts, detail, audit, diagnostics, correlation, scenarios):
    """Embed model outputs and optional public claims for offline viewing."""
    frames = {
        "history": pharma[["Month", "Brand_Name", "Manufacturer", "Molecule", "TRx"]],
        "nutrition_history": supplements[["Month", "Supplement_Category", "Total_Sales_USD"]],
        "forecasts": forecasts,
        "detail": detail,
        "audit": audit,
        "diagnostics": diagnostics,
        "correlation": correlation,
        "scenarios": scenarios,
    }
    data = {name: json.loads(frame.to_json(orient="records", date_format="iso"))
            for name, frame in frames.items()}
    cms_path = os.environ.get("GLP1_MEDICARE_DATA")
    path.parent.mkdir(parents=True, exist_ok=True)
    if cms_path:
        data["medicare"] = json.loads(Path(cms_path).read_text(encoding="utf-8"))
        (path.parent / "medicare.json").write_text(
            json.dumps(data["medicare"], indent=2, allow_nan=False), encoding="utf-8"
        )
    medicaid_path = os.environ.get("GLP1_MEDICAID_DATA")
    if medicaid_path:
        claims = json.loads(Path(medicaid_path).read_text(encoding="utf-8"))
        data["medicaid"] = claims
        (path.parent / "medicaid.json").write_text(
            json.dumps(claims, indent=2, allow_nan=False), encoding="utf-8"
        )
    payload = json.dumps(data, allow_nan=False).replace("<", "\\u003c")
    template = files("glp1_market").joinpath("dashboard.html").read_text(encoding="utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(template.replace("__PIPELINE_DATA__", payload), encoding="utf-8")
