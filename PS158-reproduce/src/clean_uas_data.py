
from pathlib import Path
import json
import pandas as pd

INPUT_FILE = Path("data/raw/uas_contracts_raw.json")
OUTPUT_FILE = Path("data/processed/uas_contracts_clean.csv")


def main():
    print("Loading expanded UAS dataset...")

    with INPUT_FILE.open("r", encoding="utf-8") as f:
        records = json.load(f)

    df = pd.DataFrame(records)

    # Convert financial fields
    df["Award Amount"] = pd.to_numeric(
        df["Award Amount"],
        errors="coerce"
    )

    # Convert dates
    for column in ["Start Date", "Last Modified Date"]:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    # Preserve API search terms as readable text
    df["Search Terms"] = df["Search Terms"].apply(
        lambda terms: "; ".join(terms)
        if isinstance(terms, list) else ""
    )

    # Remove duplicates using the API's internal ID
    df = df.drop_duplicates(subset=["internal_id"])

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(OUTPUT_FILE, index=False)

    print("\n--- CLEANING SUMMARY ---")
    print(f"Cleaned records: {len(df):,}")
    print(f"Unique contractors: {df['Recipient Name'].nunique():,}")
    print(f"Missing descriptions: {df['Description'].isna().sum():,}")
    print(f"Missing award amounts: {df['Award Amount'].isna().sum():,}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
