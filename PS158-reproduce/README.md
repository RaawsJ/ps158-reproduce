# UAS and Counter-UAS Defense Acquisition Trends

This project visualizes reported Department of Defense contract award values associated with Unmanned Aircraft Systems (UAS), Counter-UAS (C-UAS), and contracts requiring additional classification review.

**Figure:** A stacked bar chart showing the total reported award value of contracts grouped by contract start year and technology category.

**Data source:** [USAspending.gov](https://www.usaspending.gov/), using its public API to retrieve Department of Defense contract records matching selected UAS and Counter-UAS search terms.

**Method:** Contract records are retrieved, deduplicated, classified using keyword-based rules, and grouped by contract start year. Reported award values are summed within each technology category.

## Reproduction

Install the Python dependencies (`pandas`, `numpy`, `matplotlib`, and `requests`), then run the project's existing scripts in sequence:

```bash
python src/fetch_data.py
python src/clean_uas_data.py
python src/classify_contracts.py
python src/plot_uas_awards.py
```

The plotting script generates `uas_award_values_by_year.png` in the project root. Run these commands from the project root with the relevant scripts in the `src` folder.

**Limitations:** The figure presents reported contract award values grouped by start year, not annual federal spending or obligations. The keyword-based search is not exhaustive, and classifications are preliminary. Results may change when the API is queried again.
