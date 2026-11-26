"""Extract public national quarterly prescription counts from Medicaid SDUD."""

import csv
import io
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen

from glp1_market.medicare import BRANDS, parse_number

SOURCES = {
    year: f"https://download.medicaid.gov/data/sdud{year}_updated"
    + ("july" if year == 2025 else "July") + "2026.csv"
    for year in range(2021, 2026)
}


def extract(rows, year):
    """Use national totals only; never reconstruct suppressed national counts."""
    brands = {brand.upper(): brand for brand in BRANDS}
    counts, hidden, seen = {}, {}, set()
    for raw in rows:
        if raw["state"].strip().upper() != "XX":
            continue
        product = raw["product_name"].strip().upper().split()
        if not product or product[0] not in brands:
            continue
        brand = brands[product[0]]
        quarter = int(raw["quarter"])
        if int(raw["year"]) != year or quarter not in range(1, 5):
            raise ValueError(f"Unexpected SDUD period: {raw['year']}, {quarter}")
        group = quarter, brand
        key = quarter, raw["utilization_type"].strip(), raw["ndc"].strip()
        if key in seen:
            raise ValueError(f"Duplicate national SDUD record: {year}, {key}")
        seen.add(key)
        flag = raw["suppression_used"].strip().lower()
        if flag in {"true", "1", "yes", "y", "t"}:
            hidden[group] = hidden.get(group, 0) + 1
            continue
        if flag not in {"false", "0", "no", "n", "f", ""}:
            raise ValueError(f"Unknown SDUD suppression flag: {flag!r}")
        number = parse_number(raw["number_of_prescriptions"])
        if number is None:
            hidden[group] = hidden.get(group, 0) + 1
        elif not number.is_integer():
            raise ValueError("Non-integer Medicaid prescription count.")
        else:
            counts[group] = counts.get(group, 0) + int(number)
    if not counts:
        raise ValueError(f"No national SDUD counts for {year}")
    result = []
    for quarter in range(1, 5):
        data = []
        for brand in BRANDS:
            key = quarter, brand
            data.append({
                "period": f"{year} Q{quarter}", "brand": brand,
                "fills": counts.get(key), "suppressed_rows": hidden.get(key, 0),
            })
        complete = all(row["fills"] is not None and row["suppressed_rows"] == 0 for row in data)
        denominator = sum(row["fills"] for row in data) if complete else 0
        result.extend({**row, "share": row["fills"] / denominator if denominator else None}
                      for row in data)
    return result


def read_year(year):
    with urlopen(SOURCES[year], timeout=90) as response:
        with io.TextIOWrapper(response, encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            reader.fieldnames = [name.strip().lower().replace(" ", "_") for name in reader.fieldnames]
            return extract(reader, year)


def main():
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = [row for annual in pool.map(read_year, SOURCES) for row in annual]
    for brand in BRANDS:
        available = [row for row in rows if row["brand"] == brand and row["fills"] is not None]
        if not available:
            raise ValueError(f"No matching published counts for {brand}")
        print(brand, len(available), "reported quarters; earliest:", available[0]["period"])
    payload = {"rows": rows, "sources": SOURCES}
    output = Path(".cache/medicaid.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, allow_nan=False), encoding="utf-8")
    print("Medicaid panel:", json.dumps(payload, allow_nan=False))


if __name__ == "__main__":
    main()
