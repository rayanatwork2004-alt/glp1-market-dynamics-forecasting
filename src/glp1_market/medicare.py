"""Build a claims panel from public CMS files and a small annual backtest."""

import csv
import io
import json
import math
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

BRANDS = ("Ozempic", "Wegovy", "Mounjaro", "Zepbound")
ANNUAL_URL = (
    "https://data.cms.gov/sites/default/files/2026-06/"
    "98218f98-166c-4723-8438-c344a4ef96a6/DSD_PTD_RY26_P04_V10_DY24_BGM.csv"
)
QUARTERLY_URL = (
    "https://data.cms.gov/data-api/v1/dataset/4ff7c618-4e40-483a-b390-c8a58c94fa15/data"
)
YEARS = range(2020, 2025)


def read_url(url):
    with urlopen(url, timeout=45) as response:
        return response.read().decode("utf-8-sig")


def parse_number(value):
    """Keep missing and suppressed values null; reject unexpected tokens."""
    s = str(value if value is not None else "").strip().replace(",", "")
    if s.casefold() in {"", "*", "**", "-", "n/a", "na", "null", ".", "suppressed", "redacted"}:
        return None
    number = float(s)
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"Unexpected CMS value: {s}")
    return number


def select_overall(rows):
    """Use the published all-manufacturer row; manufacturer rows overlap it."""
    brands = {brand.casefold(): brand for brand in BRANDS}
    for row in rows:
        brand = brands.get(row["Brnd_Name"].strip().casefold())
        if brand and row["Mftr_Name"].strip().casefold() == "overall":
            yield brand, row


def record(brand, period, row, suffix=""):
    claims = parse_number(row["Tot_Clms" + suffix])
    spending = parse_number(row["Tot_Spndng" + suffix])
    if claims is not None and not claims.is_integer():
        raise ValueError(f"Non-integer claim count: {brand}, {period}")
    # A zero or blank does not establish that there were no fills. The CMS
    # table may omit a brand/period or hide metrics for very small counts.
    available = claims is not None and claims > 0
    return {
        "brand": brand,
        "period": period,
        "fills": int(claims) if available else None,
        "spending": spending if available else None,
    }


def complete_panel(rows, periods):
    index = {}
    for row in rows:
        key = row["period"], row["brand"]
        if key in index:
            raise ValueError(f"Duplicate CMS overall row: {key}")
        index[key] = row
    result = []
    for period in periods:
        records = [
            index.get((period, brand), {"brand": brand, "period": period, "fills": None, "spending": None})
            for brand in BRANDS
        ]
        total = sum(row["fills"] for row in records) if all(row["fills"] is not None for row in records) else None
        result.extend({**row, "share": row["fills"] / total if total else None} for row in records)
    return result


def annual_backtest(rows):
    """Compare persistence and linear drift on identical one-year targets."""
    trials = []
    eligibility = []
    for brand in BRANDS:
        history = [row for row in rows if row["brand"] == brand]
        # Use the latest consecutive run. An unavailable year resets it.
        observed = []
        for row in history:
            if row["fills"] is None:
                observed = []
            else:
                observed.append(row)
        eligibility.append({"brand": brand, "years": len(observed)})
        if len(observed) < 5:
            continue
        for i in range(2, len(observed)):
            first, last = observed[0], observed[i - 1]
            actual = observed[i]
            drift = (last["fills"] - first["fills"]) / (i - 1)
            trials.append({
                "brand": brand, "period": actual["period"], "actual": actual["fills"],
                "last": last["fills"], "drift": max(0, last["fills"] + drift),
            })
    return eligibility, trials


def build():
    annual_rows = csv.DictReader(io.StringIO(read_url(ANNUAL_URL)))
    annual = complete_panel(
        (record(brand, str(year), row, f"_{year}")
         for brand, row in select_overall(annual_rows) for year in YEARS),
        [str(year) for year in YEARS],
    )
    if any(not any(row["brand"] == brand and row["fills"] is not None for row in annual) for brand in BRANDS):
        raise ValueError("Expected at least one usable annual observation per brand.")
    preliminary = []
    for brand in BRANDS:
        query = urlencode({"filter[Brnd_Name]": brand, "filter[Mftr_Name]": "Overall", "size": 100})
        records = json.loads(read_url(f"{QUARTERLY_URL}?{query}"))
        if not isinstance(records, list) or len(records) == 100:
            raise ValueError("Unexpected or truncated CMS preliminary response.")
        for name, row in select_overall(records):
            if name != brand:
                raise ValueError(f"Unexpected CMS brand: {name}")
            label = str(row["Year"]).strip()
            if not re.fullmatch(r"20\d{2}(?:\s*\(Q[1-4](?:\s*[-–]\s*Q[1-4])?\))?", label):
                raise ValueError(f"Unexpected CMS period: {label!r}")
            preliminary.append(record(name, label, row))
    periods = sorted({row["period"] for row in preliminary})
    if not periods:
        raise ValueError("CMS returned no selected brands in the preliminary release.")
    preliminary = complete_panel(preliminary, periods)
    eligibility, trials = annual_backtest(annual)
    return {"annual": annual, "preliminary": preliminary, "eligibility": eligibility,
            "trials": trials, "annual_source": ANNUAL_URL, "preliminary_source": QUARTERLY_URL}


def main():
    output = Path(".cache/medicare.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    data = build()
    payload = json.dumps(data, ensure_ascii=True, allow_nan=False)
    output.write_text(payload, encoding="utf-8")
    # Summarize published aggregates in the build log for source verification.
    print("CMS panel:", payload)


if __name__ == "__main__":
    main()
