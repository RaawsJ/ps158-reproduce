
from pathlib import Path
import re
import pandas as pd

INPUT = Path("data/processed/uas_contracts_clean.csv")
OUTPUT = Path("data/processed/uas_contracts_classified.csv")

# Specific evidence of UAS or Counter-UAS technologies
COUNTER_UAS = [
    "counter-uas", "counter uas", "counter-uav",
    "counter drone", "counter-drone",
    "counter unmanned", "c-uas", "c-suas",
    "drone defeat", "drone detection",
    "anti-drone", "anti uas"
]

UAS = [
    "unmanned aircraft", "unmanned aerial",
    "unmanned aviation", "unmanned air system",
    "unmanned aerial vehicle", "uav", "uas",
    "drone", "remotely piloted aircraft",
    "loitering munition", "mq-9", "mq-1c",
    "mq-4c", "rq-7", "rq-11", "rq-21"
]

ACTIVITIES = {
    "Sustainment": [
        "sustainment", "logistics support",
        "maintenance", "repair", "spare parts",
        "performance based logistics"
    ],
    "Procurement": [
        "procurement", "production",
        "manufacture", "purchase",
        "full rate production", "lrip"
    ],
    "Research & Development": [
        "research", "development", "prototype",
        "demonstration", "experimentation"
    ]
}


def matched_terms(text, terms):
    found = []

    for term in terms:
        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(term)
            + r"(?![a-z0-9])"
        )
        if re.search(pattern, text):
            found.append(term)

    return found


def classify(row):
    description = str(row.get("Description", "")).lower()

    if description == "nan":
        description = ""

    counter_hits = matched_terms(description, COUNTER_UAS)
    uas_hits = matched_terms(description, UAS)

    if counter_hits:
        technology = "Counter-UAS"
    elif uas_hits:
        technology = "UAS"
    else:
        technology = "Needs Review"

    activity_hits = {
        name: matched_terms(description, terms)
        for name, terms in ACTIVITIES.items()
    }

    activities = [
        name for name, hits in activity_hits.items()
        if hits
    ]

    activity = (
        "; ".join(activities)
        if activities else "Unspecified"
    )

    evidence = sorted(set(counter_hits + uas_hits))

    review = (
        "Yes" if technology == "Needs Review"
        or len(activities) > 1
        else "No"
    )

    return pd.Series({
        "Technology Category": technology,
        "Acquisition Activity": activity,
        "Matched Evidence": "; ".join(evidence),
        "Review Required": review
    })


def main():
    df = pd.read_csv(INPUT)

    classifications = df.apply(classify, axis=1)
    df = pd.concat([df, classifications], axis=1)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)

    print("\n--- TECHNOLOGY CLASSIFICATION ---")
    print(df["Technology Category"].value_counts())

    print("\n--- ACQUISITION ACTIVITIES ---")
    print(df["Acquisition Activity"].value_counts().head(15))

    print("\n--- REVIEW SUMMARY ---")
    print(df["Review Required"].value_counts())

    print(f"\nTotal records: {len(df):,}")
    print(f"Saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
