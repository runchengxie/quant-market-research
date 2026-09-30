"""Browser check for overview, legacy redirect, and native research navigation."""
import sys

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 1100})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(sys.argv[1], wait_until="domcontentloaded")
    cards = page.get_by_role("region", name="Research progress by topic")
    cards.wait_for(timeout=10000)
    assert cards.locator("article").count() == 3
    assert page.locator("main table, main canvas, main iframe").count() == 0
    assert page.locator('a[href*="recovery.html"]').count() == 0
    for width in [1440, 390]:
        page.set_viewport_size({"width": width, "height": 1100})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
        page.locator("main").screenshot(path=f"/tmp/quant-overview-{width}.png")
    page.goto(sys.argv[1] + "research/recovery.html", wait_until="domcontentloaded")
    page.wait_for_url("**/#cashflow-recovery")
    recovery = page.get_by_role("region", name="Recovery and holding-period risk")
    recovery.wait_for()
    assert "CSI 800 Cash Flow" in recovery.inner_text()
    page.wait_for_function("Math.abs(document.querySelector('#cashflow-recovery')?.getBoundingClientRect().top ?? Infinity) < 60")
    recovery.get_by_text("Method and reading notes", exact=True).click()
    assert recovery.get_by_text("The gain needed to recover is the prior high divided by the current level, minus one. For example, a 50% loss requires a 100% gain to break even.", exact=True).is_visible()
    recovery.get_by_role("link", name="View micro-cap recovery research ↗").click()
    page.locator('#microcap-recovery').wait_for()
    assert "Tonghuashun Micro-cap" in recovery.inner_text()
    page.get_by_role("button", name="Cross-market micro-cap liquidity", exact=True).click()
    page.get_by_role("link", name="Cash-flow history", exact=True).click()
    page.locator('#cashflow-recovery').wait_for()
    recovery.get_by_role("link", name="View micro-cap recovery research ↗").click()
    page.locator('#microcap-recovery').wait_for(timeout=10000)
    recovery.get_by_role("link", name="View cash-flow recovery research ↗").click()
    page.locator('#cashflow-recovery').wait_for()
    page.wait_for_function("Math.abs(document.querySelector('#cashflow-recovery')?.getBoundingClientRect().top ?? Infinity) < 60")
    page.get_by_role("link", name="Research overview", exact=True).click()
    cards.wait_for()
    assert page.locator("main table, main canvas").count() == 0
    assert not errors, errors
    browser.close()
    print("PASS: summary-only overview, mobile, legacy redirect, methods and cross-topic navigation")
