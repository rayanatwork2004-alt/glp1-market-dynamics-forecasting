"""Export a portable dashboard from the same data used by the pipeline."""

import json
from importlib.resources import files


def write_dashboard(path, pharma, supplements, forecasts, detail, audit, diagnostics, correlation, scenarios):
    """Embed only synthetic outputs so the dashboard can open offline."""
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
    payload = json.dumps(data, allow_nan=False).replace("<", "\\u003c")
    template = files("glp1_market").joinpath("dashboard.html").read_text(encoding="utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(template.replace("__PIPELINE_DATA__", payload), encoding="utf-8")
