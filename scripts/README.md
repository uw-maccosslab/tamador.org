# TaMADOR Scripts

This directory contains utility scripts for maintaining the TaMADOR website.

## fetch_publications.py

Automatically fetches and updates publications from PubMed that acknowledge TaMADOR grant funding.

### What it does:

1. Queries PubMed for papers crediting the TaMADOR grants:
   - U01 DK137097 (University of Washington)
   - U01 DK137113 (Pacific Northwest National Laboratories)
   - U01 DK124020 (Pacific Northwest National Laboratories)
   - U01 DK124019 (Cedars-Sinai Medical Center)

2. Includes additional specific PMIDs that may not be found by grant number search:
   - PMID: 40802520
   - PMID: 40093566
   - PMID: 40739343
   - PMID: 38109936

3. Updates `publications.md` with the latest publication list

4. Generates a bar chart showing publications per year (`assets/images/publication-metrics.png`)

### Requirements:

```bash
pip install requests matplotlib
```

### Usage:

```bash
# Run from anywhere
python scripts/fetch_publications.py

# Or make it executable and run directly
chmod +x scripts/fetch_publications.py
./scripts/fetch_publications.py
```

### Automation:

You can set up a cron job or GitHub Action to run this script periodically (e.g., weekly) to keep publications automatically updated:

```bash
# Example cron: Run every Monday at 9 AM
0 9 * * 1 cd /path/to/tamador.org && python scripts/fetch_publications.py
```

### Output:

- Updates `publications.md` with current publication list
- Creates/updates `assets/images/publication-metrics.png` with publications-per-year chart
- Preserves the file header and formatting

### Notes:

- The script uses NCBI E-utilities API (no API key required for moderate use)
- Be respectful of NCBI's rate limits (3 requests/second without API key)
- Publications are sorted by year in reverse chronological order
- The plot uses the website's color scheme (blue: #2c5282)
- To add more PMIDs manually, edit the `ADDITIONAL_PMIDS` list in the script
