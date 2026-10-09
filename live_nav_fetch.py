import csv
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
REPORT_DIR = BASE_DIR / "reports"

SCHEMES = {
    "HDFC_Top_100_Direct": {
        "code": "125497",
        "expected": ["HDFC", "TOP 100"],
    },
    "SBI_Bluechip": {
        "code": "119598",
        "expected": ["SBI", "LARGE CAP"],
    },
    "ICICI_Bluechip": {
        "code": "120586",
        "expected": ["ICICI PRUDENTIAL", "LARGE CAP"],
    },
    "Nippon_Large_Cap": {
        "code": "118632",
        "expected": ["NIPPON INDIA", "LARGE CAP"],
    },
    "Axis_Bluechip": {
        "code": "120465",
        "expected": ["AXIS", "LARGE CAP"],
    },
    "Kotak_Bluechip": {
        "code": "120152",
        "expected": ["KOTAK", "LARGE CAP"],
    },
}


def fetch_scheme(name, details):
    code = details["code"]
    url = f"https://api.mfapi.in/mf/{code}"

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()

    metadata = payload.get("meta", {})
    actual_name = metadata.get("scheme_name", "Unknown scheme")
    nav_records = payload.get("data", [])

    if not nav_records:
        raise ValueError("API returned no NAV records.")

    expected = details["expected"]
    actual_upper = actual_name.upper()

    if not all(term in actual_upper for term in expected):
        # Preserve the returned data under its actual identity.
        output_file = RAW_DIR / f"live_nav_unmatched_code_{code}.csv"
        write_nav_csv(output_file, code, actual_name, nav_records)

        return (
            f"MISMATCH: {name}, code {code}\n"
            f"Expected scheme keywords: {expected}\n"
            f"Actual scheme name: {actual_name}\n"
            f"Returned data saved to: {output_file}\n"
        )

    output_file = RAW_DIR / f"live_nav_{name}.csv"
    write_nav_csv(output_file, code, actual_name, nav_records)

    print(f"SUCCESS: {name}")
    print(f"  Scheme: {actual_name}")
    print(f"  NAV records: {len(nav_records)}")
    print(f"  Saved: {output_file}")

    return None


def write_nav_csv(output_file, code, scheme_name, records):
    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["scheme_code", "scheme_name", "date", "nav"])

        for record in records:
            writer.writerow([
                code,
                scheme_name,
                record.get("date", ""),
                record.get("nav", ""),
            ])


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    issues = []

    for name, details in SCHEMES.items():
        try:
            issue = fetch_scheme(name, details)
            if issue:
                issues.append(issue)
                print(issue)
        except (requests.RequestException, ValueError, KeyError) as error:
            message = f"FAILED: {name}, code {details['code']}: {error}"
            issues.append(message)
            print(message)

    report_file = REPORT_DIR / "live_nav_fetch_issues.txt"

    if issues:
        report_file.write_text(
            "LIVE NAV FETCH ISSUES\n\n" + "\n".join(issues),
            encoding="utf-8",
        )
        print(f"\nCompleted with issues. See: {report_file}")
    else:
        report_file.write_text(
            "All six requested scheme identities were verified successfully.\n",
            encoding="utf-8",
        )
        print("\nAll six schemes verified successfully.")


if __name__ == "__main__":
    main()
