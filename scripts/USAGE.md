# Running the Publication Fetcher

## Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the script
python scripts/fetch_publications.py

# Deactivate when done
deactivate
```

## What the Script Does

The `fetch_publications.py` script:

1. **Queries PubMed** for all papers crediting TaMADOR grants
2. **Fetches 59 distinct papers** (as of Aug 2026) across 9 years (2018-2026):
   57 peer reviewed plus 2 preprints not yet peer reviewed
3. **Collapses preprint duplicates**, keeping the peer-reviewed version of any
   paper that has one. Pairs PubMed does not link are listed in
   `SUPERSEDED_PREPRINTS`
4. **Updates publications.md** with formatted publication list
5. **Generates a chart** of peer-reviewed publications and preprints per year

## Output Files

- `publications.md` - Updated with current publication list
- `assets/images/publication-metrics.png` - Stacked bar chart of peer-reviewed
  publications and preprints per year

## Automation

### Weekly Updates (Recommended)

Set up a cron job to run weekly:

```bash
# Edit crontab
crontab -e

# Add this line (runs every Monday at 9 AM)
0 9 * * 1 cd /path/to/tamador.org && .venv/bin/python scripts/fetch_publications.py
```

### GitHub Action (Alternative)

Create `.github/workflows/update-publications.yml`:

```yaml
name: Update Publications

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM
  workflow_dispatch:  # Allow manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run publication fetcher
        run: python scripts/fetch_publications.py

      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add publications.md assets/images/publication-metrics.png
          git diff --quiet && git diff --staged --quiet || git commit -m "Auto-update publications"
          git push
```

## Customization

Edit `scripts/fetch_publications.py` to:

- Change grant numbers (`GRANT_NUMBERS`)
- Add papers the grant search misses (`ADDITIONAL_PMIDS`)
- Record a preprint/published pair PubMed does not link (`SUPERSEDED_PREPRINTS`)
- Modify plot styling (`generate_publications_plot`)
- Adjust publication formatting (`update_publications_file`)

## Troubleshooting

### Error: "No module named 'requests'"
```bash
pip install -r requirements.txt
```

### Error: "Connection timeout"
NCBI E-utilities may be rate-limiting. Wait a few minutes and try again.

### Empty publication list
Verify grant numbers are correct in the script. Check PubMed manually:
https://pubmed.ncbi.nlm.nih.gov/?term=%22U01+DK137097%22%5BGrant+Number%5D
