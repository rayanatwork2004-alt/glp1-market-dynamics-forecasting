"""Check the generated dashboard in Chromium before publication.

Run after the pipeline with python tests/check_dashboard_browser.py.
Requires playwright and its Chromium browser, installed by GitHub Actions.
"""

import copy
import json
import math
import re
import tempfile
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


def option_values(page, selector):
    return page.locator(selector + " option").evaluate_all(
        "options => options.map(option => option.value)"
    )


def choose(page, selector, value):
    page.locator(selector).select_option(value)


def assert_valid_charts(page):
    invalid = page.locator("svg").evaluate_all(
        """charts => charts.flatMap(chart => [...chart.querySelectorAll("*")])
            .flatMap(node => [...node.attributes].map(attribute => attribute.value))
            .some(value => /NaN|Infinity|undefined/.test(value))"""
    )
    assert not invalid, "A chart contains invalid coordinates or labels"


def check_medicaid(page):
    positions = []
    for period in option_values(page, "#sdud-period"):
        choose(page, "#sdud-period", period)
        marker = page.locator('#sdud-chart rect[data-selected-period]')
        expect(marker).to_have_attribute("data-selected-period", period)
        positions.append(float(marker.get_attribute("x")))
        expect(page.locator("#sdud-table caption")).to_have_text(period)
        expect(page.locator("#sdud-status")).to_contain_text(period)
    assert len(set(positions)) == len(positions), "Quarter marker did not move"


def check_controls(page, data):
    for metric in option_values(page, "#cms-metric"):
        choose(page, "#cms-metric", metric)
        for period in option_values(page, "#cms-period"):
            choose(page, "#cms-period", period)
            expect(page.locator("#cms-table caption")).to_have_text(period)
            expect(page.locator("#cms-table tbody tr")).to_have_count(
                len(data["medicare"]["eligibility"])
            )
            expect(page.locator("#cms-period-chart")).to_contain_text(period)
            if period in {row["period"] for row in data["medicare"]["annual"]}:
                marker = page.locator("#cms-chart rect[data-selected-period]")
                if page.locator("#cms-chart svg").count():
                    expect(marker).to_have_attribute("data-selected-period", period)
            else:
                expect(page.locator("#cms-chart rect[data-selected-period]")).to_have_count(0)
                expect(page.locator("#cms-chart-note")).to_contain_text("preliminary")

    check_medicaid(page)
    for segment in option_values(page, "#segment"):
        choose(page, "#segment", segment)
        for horizon in option_values(page, "#horizon"):
            choose(page, "#horizon", horizon)
            expect(page.locator("#forecast-chart h3")).to_contain_text(
                "next " + horizon + " months"
            )
            expect(page.locator("#forecast-status")).to_contain_text(segment)
            titles = page.locator("#forecast-chart circle title").all_text_contents()
            assert sum(title.startswith("Forecast ·") for title in titles) == int(horizon)
            trials = [
                row for row in data["detail"]
                if row["Segment"] == segment and row["Horizon"] == int(horizon)
            ]
            dates = {row["Month"] for row in trials}
            expect(page.locator("#forecast-status")).to_contain_text(
                str(len(dates)) + " distinct test"
            )
            if trials:
                expected_points = len(dates) + sum(
                    isinstance(row["Prediction"], (float, int))
                    and math.isfinite(row["Prediction"]) for row in trials
                )
                expect(page.locator("#held-out circle")).to_have_count(expected_points)
            assert_valid_charts(page)

    for scenario in option_values(page, "#case"):
        choose(page, "#case", scenario)
        expect(page.locator("#scenario-chart h3")).to_contain_text(scenario)
        rows = [row for row in data["scenarios"] if row["Scenario"] == scenario]
        expect(page.locator("#assumptions")).to_have_text(rows[-1]["Assumptions"])
        expect(page.locator("#scenario-cards .card")).to_have_count(5)

    for cost in option_values(page, "#cost-option"):
        choose(page, "#cost-option", cost)
        values = page.locator("#cost-cards strong").all_text_contents()
        assert values == ["$149", "$" + cost, "$" + str(149 - int(cost))]

    for selector, key in [("#cms-data-download", "medicare"), ("#sdud-download", "medicaid")]:
        with page.expect_download() as download:
            page.locator(selector).click()
        assert json.loads(Path(download.value.path()).read_text()) == data[key]

    for link in page.locator("nav a").all():
        if link.is_visible():
            link.click()
            assert page.evaluate("location.hash") == link.get_attribute("href")

    page.set_viewport_size({"width": 390, "height": 844})
    check_medicaid(page)
    overflow = page.locator("body *").evaluate_all(
        """nodes => nodes.filter(node => {
            const box = node.getBoundingClientRect();
            return box.width && box.right > innerWidth + 1 &&
                !node.closest(".scroller") && !node.closest("nav") && !node.closest("svg");
        }).map(node => ({tag:node.tagName,id:node.id,width:node.getBoundingClientRect().width}))"""
    )
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), overflow
    select = page.locator("#sdud-period")
    periods = option_values(page, "#sdud-period")
    choose(page, "#sdud-period", periods[0])
    select.focus()
    select.press("ArrowDown")
    select.press("Enter")
    expect(select).to_have_value(periods[1])
    expect(page.locator("#sdud-table caption")).to_have_text(periods[1])
    expect(page.locator("#sdud-chart rect[data-selected-period]")).to_have_attribute(
        "data-selected-period", periods[1]
    )


def main():
    dashboard = Path("outputs/dashboard.html").resolve()
    html = dashboard.read_text(encoding="utf-8")
    match = re.search(r'<script type="application/json" id="data">(.*?)</script>', html, re.S)
    assert match, "Dashboard payload is missing"
    data = json.loads(match.group(1))
    assert data.get("medicare") and data.get("medicaid"), "Public claims panels are required for this check"

    with sync_playwright() as playwright, tempfile.TemporaryDirectory() as temporary:
        browser = playwright.chromium.launch()
        page = browser.new_page(accept_downloads=True, viewport={"width": 1280, "height": 900})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(dashboard.as_uri())
        check_controls(page, data)

        # An offline build can omit public panels and have no eligible backtests.
        limited = copy.deepcopy(data)
        limited.pop("medicare")
        limited["medicaid"] = {"rows": []}
        limited["detail"] = []
        limited["audit"] = []
        limited["diagnostics"] = []
        fixture = Path(temporary) / "limited.html"
        payload = json.dumps(limited).replace("<", "\\u003c")
        fixture.write_text(html[:match.start(1)] + payload + html[match.end(1):], encoding="utf-8")
        page.goto(fixture.as_uri())
        expect(page.locator("#cms-offline")).to_be_visible()
        expect(page.locator('nav a[href="#medicaid"]')).to_be_hidden()
        expect(page.locator("#held-out")).to_contain_text("Insufficient history")
        expect(page.locator("#audit")).to_contain_text("No results available")
        choose(page, "#cost-option", "50")
        expect(page.locator("#cost-cards strong").nth(1)).to_have_text("$50")
        choose(page, "#horizon", "6")
        expect(page.locator("#forecast-chart h3")).to_contain_text("next 6 months")
        assert_valid_charts(page)
        assert not errors, errors
        browser.close()
    print("Browser checks passed for all selectors, downloads, mobile layout, keyboard input, and missing optional data.")


if __name__ == "__main__":
    main()
