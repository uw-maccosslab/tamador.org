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
2. **Fetches 52 publications** (as of Feb 2026) across 8 years (2018-2025)
3. **Updates publications.md** with formatted publication list
4. **Generates a chart** showing publications per year

## Output Files

- `publications.md` - Updated with current publication list
- `assets/images/publication-metrics.png` - Bar chart of pubs per year

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

- Change grant numbers (lines 19-24)
- Modify plot styling (lines 285-330)
- Adjust publication formatting (lines 194-210)

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
