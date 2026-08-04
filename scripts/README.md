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

   The query searches the bare grant number (`DK137097[Grant Number]`) rather than
   the full `U01 DK137097` string. PubMed matches this field literally, and records
   store the grant several ways (`U01 DK137097`, `U01DK137097`, or inside a
   free-text blob), so the full-string form silently misses papers.

3. Collapses preprint/published duplicates. A bioRxiv preprint and the article it
   becomes are separate PubMed records; listing both double-counts the paper. Any
   preprint PubMed links to a published version is replaced by that version, which
   is fetched explicitly if the grant search missed it. Preprints with no published
   version yet are kept and counted separately.

4. Updates `publications.md` with the latest publication list, newest first within
   each year. Preprints are marked `(preprint, not peer reviewed)`.

5. Generates a stacked bar chart of peer-reviewed publications and preprints per
   year (`assets/images/publication-metrics.png`)

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
