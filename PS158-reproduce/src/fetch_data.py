
from pathlib import Path
import json
import time
import requests

API_URL = (
    "https://api.usaspending.gov/api/v2/"
    "search/spending_by_award/"
)

OUTPUT_FILE = Path("data/raw/uas_contracts_raw.json")

SEARCH_TERMS = [
    "unmanned aircraft",
    "unmanned aerial",
    "UAV",
    "drone",
    "counter-UAS",
    "counter drone",
    "loitering munition",
    "MQ-9",
    "MQ-1C",
    "small unmanned aircraft"
]

PAGE_SIZE = 100
MAX_PER_TERM = 500

FIELDS = [
    "Award ID",
    "Recipient Name",
    "Award Amount",
    "Awarding Agency",
    "Awarding Sub Agency",
    "Description",
    "PSC",
    "NAICS",
    "Start Date",
    "Last Modified Date"
]


def make_payload(term, page):
    return {
        "filters": {
            "agencies": [{
                "type": "awarding",
                "tier": "toptier",
                "name": "Department of Defense"
            }],
            "time_period": [{
                "start_date": "2020-10-01",
                "end_date": "2026-09-30"
            }],
            "award_type_codes": ["A", "B", "C", "D"],
            "keywords": [term]
        },
        "fields": FIELDS,
        "page": page,
        "limit": PAGE_SIZE,
        "sort": "Award Amount",
        "order": "desc",
        "subawards": False
    }


def main():
    awards = {}
    failed_terms = []

    with requests.Session() as session:
        for term in SEARCH_TERMS:
            print(f"\nSearching: {term}", flush=True)
            retrieved = 0
            page = 1

            while retrieved < MAX_PER_TERM:
                payload = make_payload(term, page)

                try:
                    response = session.post(
                        API_URL,
                        json=payload,
                        timeout=60
                    )
                    response.raise_for_status()
                    data = response.json()

                except (
                    requests.RequestException,
                    ValueError
                ) as error:
                    print(f"Request failed: {error}")
                    if (
                        response is not None
                        and not response.ok
                    ):
                        print(response.text[:500])
                    failed_terms.append(term)
                    break

                records = data.get("results", [])

                if not records:
                    break

                for record in records:
                    # Internal ID identifies an award record
                    award_id = (
                        record.get("internal_id")
                        or record.get("generated_internal_id")
                        or record.get("Award ID")
                    )

                    if not award_id:
                        continue

                    key = str(award_id)

                    if key not in awards:
                        saved = record.copy()
                        saved["Search Terms"] = []
                        awards[key] = saved

                    if term not in awards[key]["Search Terms"]:
                        awards[key]["Search Terms"].append(term)

                retrieved += len(records)

                print(
                    f"Page {page}: {retrieved} retrieved, "
                    f"{len(awards)} unique awards",
                    flush=True
                )

                metadata = data.get("page_metadata", {})

                if (
                    len(records) < PAGE_SIZE
                    or metadata.get("hasNext") is False
                ):
                    break

                page += 1
                time.sleep(0.5)

    if not awards:
        print("No records collected. Existing file unchanged.")
        return

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            list(awards.values()),
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\n--- DOWNLOAD SUMMARY ---")
    print(f"Unique contract records: {len(awards)}")
    print(f"Search terms attempted: {len(SEARCH_TERMS)}")
    print(f"Failed terms: {failed_terms}")
    print(f"Saved to: {OUTPUT_FILE}")

    if failed_terms:
        print("WARNING: Dataset is incomplete.")


if __name__ == "__main__":
    main()
