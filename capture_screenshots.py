"""Optional browser evidence capture. Requires Playwright and its Chromium."""
import argparse
import json
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright, expect
from copilot.core import Copilot, Snapshot, REFUSAL
from copilot.server import make_server

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--out", default="evidence/screenshots")
    args = p.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    data = json.loads(Path(__file__).with_name("evidence").joinpath("query-response-transcripts.json").read_text(encoding="utf-8"))
    cases = {item["case"]:item["question"] for item in data}
    with make_server(Copilot(Snapshot(args.repo)), 0) as server:
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width":1360,"height":1000})
                page.goto(f"http://127.0.0.1:{server.server_port}")
                for case, name, card in [
                    ("Q01","01-auth-expanded-citation.png",1),
                    ("Q02","02-database-retry.png",0),
                    ("Q09","03-stripe-rejected.png",None),
                ]:
                    page.get_by_label("Developer question").fill(cases[case])
                    with page.expect_response(lambda res: res.url.endswith("/api/ask")):
                        page.get_by_role("button",name="Search code").click()
                    expect(page.locator("#result")).to_be_visible()
                    if card is None:
                        expect(page.locator("#answer")).to_have_text(REFUSAL)
                        expect(page.locator("details")).to_have_count(0)
                    else:
                        expect(page.locator("#badge")).to_have_text("Cited answer")
                        page.locator("summary").nth(card).click()
                        expect(page.locator("details[open] .highlight").first).to_be_visible()
                        if case == "Q01":
                            assert page.locator("details[open] .line").all_text_contents() == [str(i) for i in range(9,17)]
                    page.screenshot(path=str(out/name), full_page=True)
                browser.close()
        finally:
            server.shutdown()
            worker.join()

if __name__ == "__main__":
    main()
