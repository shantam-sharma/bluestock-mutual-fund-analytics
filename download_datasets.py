
from pathlib import Path
from urllib.request import urlopen, Request

ROOT = Path(__file__).resolve().parent

FILES = {
    "data/raw/08_investor_transactions.csv":
        "https://assets.validstep.com/workspace/shared-datasets/3430cd3b-bd90-492f-8c47-7d03c166b37c/1788499980509-304c1255-08_investor_transactions.csv",
    "data/raw/09_portfolio_holdings.csv":
        "https://assets.validstep.com/workspace/shared-datasets/3430cd3b-bd90-492f-8c47-7d03c166b37c/1788499982117-e3d6ab98-09_portfolio_holdings.csv",
    "data/raw/10_benchmark_indices.csv":
        "https://assets.validstep.com/workspace/shared-datasets/3430cd3b-bd90-492f-8c47-7d03c166b37c/1788499982615-f9647ab2-10_benchmark_indices.csv",
    "data/raw/01_fund_master.csv":
        "https://assets.validstep.com/workspace/shared-datasets/3430cd3b-bd90-492f-8c47-7d03c166b37c/1788499983024-b042c300-01_fund_master.csv",
    "data/raw/02_nav_history.csv":
        "https://assets.validstep.com/workspace/shared-datasets/3430cd3b-bd90-492f-8c47-7d03c166b37c/1788499983331-4389156d-02_nav_history.csv",
    "data/raw/04_monthly_sip_inflows.csv":
        "https://assets.validstep.com/workspace/shared-datasets/3430cd3b-bd90-492f-8c47-7d03c166b37c/1788499984405-d702a6c6-04_monthly_sip_inflows.csv",
    "data/raw/05_category_inflows.csv":
        "https://assets.validstep.com/workspace/shared-datasets/3430cd3b-bd90-492f-8c47-7d03c166b37c/1788499984721-4b860901-05_category_inflows.csv",
    "data/raw/06_industry_folio_count.csv":
        "https://assets.validstep.com/workspace/shared-datasets/3430cd3b-bd90-492f-8c47-7d03c166b37c/1788499985036-da4a0c4a-06_industry_folio_count.csv",
    "data/raw/07_scheme_performance.csv":
        "https://assets.validstep.com/workspace/shared-datasets/3430cd3b-bd90-492f-8c47-7d03c166b37c/1788499985420-bb134abf-07_scheme_performance.csv",
    "data/raw/03_aum_by_fund_house.csv":
        "https://assets.validstep.com/workspace/shared-datasets/3430cd3b-bd90-492f-8c47-7d03c166b37c/1788499984134-b0cbf625-03_aum_by_fund_house.csv",
    "Documentation/Preboarding_-_BF.pdf":
        "https://assets.validstep.com/workspace/shared-datasets/3430cd3b-bd90-492f-8c47-7d03c166b37c/1788501177869-735e8224-Preboarding_-_BF.pdf",
    "Documentation/Bluestock_MF_Capstone_Project.pdf":
        "https://assets.validstep.com/workspace/shared-datasets/3430cd3b-bd90-492f-8c47-7d03c166b37c/1788499980090-36444421-Bluestock_MF_Capstone_Project.pdf",
}


def download_file(relative_path, url):
    destination = ROOT / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)

    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    try:
        with urlopen(request, timeout=60) as response:
            content = response.read()

        if not content:
            raise ValueError("Downloaded file is empty.")

        # Avoid saving an error page as a CSV or PDF.
        if content.lstrip().lower().startswith(
            (b"<!doctype html", b"<html")
        ):
            raise ValueError("Server returned HTML instead of the file.")

        destination.write_bytes(content)
        print(f"Downloaded: {relative_path} ({len(content):,} bytes)")

    except Exception as error:
        print(f"FAILED: {relative_path} — {error}")


if __name__ == "__main__":
    for path, url in FILES.items():
        download_file(path, url)

    print("\nDownload attempt finished. Check any FAILED messages.")
