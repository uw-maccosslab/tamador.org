#!/usr/bin/env python3
"""
Fetch publications from PubMed for TaMADOR grants and update publications.md

This script uses the NCBI E-utilities API to fetch publications that credit
the TaMADOR grant numbers and updates the publications page. It also generates
a plot showing publications per year.

Grant numbers:
- U01 DK137097 (University of Washington)
- U01 DK137113 (Pacific Northwest National Laboratories)
- U01 DK124020 (Pacific Northwest National Laboratories)
- U01 DK124019 (Cedars-Sinai Medical Center)

Additionally includes specific PMIDs that may not be found by grant number search.
"""

import requests
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server/CI
import matplotlib.pyplot as plt

# Configuration
GRANT_NUMBERS = [
    'U01 DK137097',
    'U01 DK137113',
    'U01 DK124020',
    'U01 DK124019'
]

# Additional PMIDs to include (publications that may not have grant numbers indexed)
ADDITIONAL_PMIDS = [
    '40802520',
    '40093566',
    '40739343',
    '38109936'
]

# Preprints superseded by a published paper that PubMed does not link.
#
# PubMed normally records the relationship with an UpdateIn reference, which
# resolve_preprints() follows on its own. Some pairs have no such reference at
# all, so the preprint and the published paper look like unrelated records. This
# is easy to miss when reviewers asked for a title change, since the two entries
# no longer share a title either. Map preprint PMID -> published PMID here.
SUPERSEDED_PREPRINTS = {
    # 'Mag-Net: Rapid enrichment of membrane-bound particles enables high
    # coverage quantitative analysis of the plasma proteome' (bioRxiv 2024)
    # was published as 'Enrichment of extracellular vesicles using Mag-Net for
    # the analysis of the plasma proteome' (Nat Commun 2025) after retitling.
    '38617345': '40595564',
}


def grant_core_number(grant):
    """Extract the core grant number (e.g. 'DK137097' from 'U01 DK137097').

    PubMed's [Grant Number] field is a literal string match against whatever the
    depositor recorded, and the same grant shows up several ways: 'U01 DK137097',
    'U01DK137097' (no space), or buried in a free-text blob such as
    'NCI:P30CA016056 / NIH: DK124020, HL103411'. Searching the bare core number
    matches all of these, whereas searching '"U01 DK137097"[Grant Number]' only
    matches the spaced form and silently drops the rest.
    """
    match = re.search(r'([A-Z]{2}\d{6,})', grant.replace(' ', ''))
    return match.group(1) if match else grant


# Build PubMed search query for grant numbers
PUBMED_SEARCH_TERM = ' OR '.join(
    [f'{grant_core_number(grant)}[Grant Number]' for grant in GRANT_NUMBERS]
)

PUBLICATIONS_FILE = Path(__file__).parent.parent / 'publications.md'
PLOT_OUTPUT_FILE = Path(__file__).parent.parent / 'assets' / 'images' / 'publication-metrics.png'
MAX_RESULTS = 500  # Fetch all publications

# NCBI E-utilities base URLs
ESEARCH_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
EFETCH_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'


def search_pubmed(query, max_results=500):
    """Search PubMed and return a list of PMIDs."""
    params = {
        'db': 'pubmed',
        'term': query,
        'retmax': max_results,
        'sort': 'date',
        'retmode': 'json'
    }

    response = requests.get(ESEARCH_URL, params=params)
    response.raise_for_status()
    data = response.json()

    return data.get('esearchresult', {}).get('idlist', [])


def fetch_publication_details(pmids):
    """Fetch detailed publication information for given PMIDs."""
    if not pmids:
        return []

    # Process in batches to avoid timeout
    batch_size = 100
    all_publications = []

    for i in range(0, len(pmids), batch_size):
        batch_pmids = pmids[i:i + batch_size]
        params = {
            'db': 'pubmed',
            'id': ','.join(batch_pmids),
            'retmode': 'xml'
        }

        response = requests.get(EFETCH_URL, params=params, timeout=60)
        response.raise_for_status()

        batch_pubs = parse_pubmed_xml(response.text)
        all_publications.extend(batch_pubs)

    return all_publications


MONTH_NUMBERS = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}


def parse_month(month_text):
    """Convert a PubMed <Month> value to an int, 0 if absent or unrecognized.

    PubMed writes months either as three-letter abbreviations ('Jul') or as
    numbers ('07'), and may omit the element entirely.
    """
    if not month_text:
        return 0
    month_text = month_text.strip()
    if month_text.isdigit():
        return int(month_text)
    return MONTH_NUMBERS.get(month_text[:3].lower(), 0)


def parse_pubmed_xml(xml_text):
    """Parse PubMed XML response and extract publication details."""
    publications = []
    root = ET.fromstring(xml_text)

    for article in root.findall('.//PubmedArticle'):
        pub = {}

        # Get PMID
        pmid = article.find('.//PMID')
        pub['pmid'] = pmid.text if pmid is not None else ''

        # Get title - use itertext() to handle embedded tags like <i>gene</i>
        title = article.find('.//ArticleTitle')
        if title is not None:
            pub['title'] = ''.join(title.itertext()).rstrip('.')
        else:
            pub['title'] = ''

        # Get authors
        authors = []
        for author in article.findall('.//Author'):
            lastname = author.find('LastName')
            initials = author.find('Initials')
            if lastname is not None:
                name = lastname.text
                if initials is not None:
                    name += ' ' + initials.text
                authors.append(name)
        pub['authors'] = ', '.join(authors)

        # Get journal
        journal = article.find('.//Journal/Title')
        pub['journal'] = journal.text if journal is not None else ''

        # Get publication date. Month/day are not displayed, but they order
        # publications within a year (see sort_key in update_publications_file).
        pub_date = article.find('.//PubDate')
        if pub_date is not None:
            year = pub_date.find('Year')
            pub['year'] = year.text if year is not None else ''
            pub['month'] = parse_month(pub_date.findtext('Month'))
            pub['day'] = int(pub_date.findtext('Day') or 0)
        else:
            pub['year'] = ''
            pub['month'] = 0
            pub['day'] = 0

        # Get DOI
        doi = None
        for article_id in article.findall('.//ArticleId'):
            if article_id.get('IdType') == 'doi':
                doi = article_id.text
                break
        pub['doi'] = doi

        # Preprint status, and the peer-reviewed article that supersedes it.
        # PubMed marks preprints with a 'Preprint' publication type and links
        # them to the final article with an 'UpdateIn' reference.
        types = {t.text for t in article.findall('.//PublicationType')}
        pub['is_preprint'] = 'Preprint' in types
        pub['published_version'] = next(
            (cc.findtext('PMID') for cc in article.findall('.//CommentsCorrections')
             if cc.get('RefType') == 'UpdateIn'),
            None
        )

        publications.append(pub)

    return publications


def resolve_preprints(publications):
    """Replace superseded preprints with their peer-reviewed versions.

    A bioRxiv preprint and the article it becomes are separate PubMed records, so
    listing both double-counts the same paper. Any preprint that names a published
    version is dropped in favour of that version. The published record sometimes
    omits the grant numbers the search relies on, so a version that the search did
    not return is fetched explicitly rather than lost. Preprints with no published
    version yet are kept and counted separately.
    """
    by_pmid = {pub['pmid']: pub for pub in publications}

    superseded = {pub['pmid']: pub['published_version'] for pub in publications
                  if pub['is_preprint'] and pub['published_version']}

    # Curated pairs PubMed does not link, applied on top of the automatic ones
    for preprint_pmid, published_pmid in SUPERSEDED_PREPRINTS.items():
        if preprint_pmid in by_pmid:
            superseded[preprint_pmid] = published_pmid
        else:
            # Flag rather than ignore, so the curated list does not quietly rot
            print(f"  NOTE: curated pair {preprint_pmid} -> {published_pmid} is no "
                  f"longer needed, that preprint is not in the results")

    if not superseded:
        return publications

    # Pull in published versions the grant search missed, so dropping the
    # preprint never drops the paper.
    missing = sorted(set(superseded.values()) - set(by_pmid))
    if missing:
        print(f"  Fetching {len(missing)} published version(s) missed by grant search: "
              f"{', '.join(missing)}")
        for pub in fetch_publication_details(missing):
            by_pmid[pub['pmid']] = pub

    for preprint_pmid, published_pmid in sorted(superseded.items()):
        if published_pmid not in by_pmid:
            # Could not retrieve the published version; keep the preprint rather
            # than silently losing the paper.
            print(f"  WARNING: keeping preprint {preprint_pmid}, could not fetch "
                  f"published version {published_pmid}")
            continue
        del by_pmid[preprint_pmid]
        print(f"  Preprint {preprint_pmid} superseded by {published_pmid}")

    return list(by_pmid.values())


def update_publications_file(publications):
    """Update publications.md with fetched publications."""
    if not publications:
        print("No publications to update")
        return False

    # Group publications by year
    pubs_by_year = {}
    for pub in publications:
        year = pub.get('year', '')
        if year:
            try:
                year = int(year)
                if year not in pubs_by_year:
                    pubs_by_year[year] = []
                pubs_by_year[year].append(pub)
            except ValueError:
                pass

    # Sort years in reverse order (newest first)
    sorted_years = sorted(pubs_by_year.keys(), reverse=True)

    # Order publications within each year, newest first. Without this the order
    # follows set iteration order, which Python randomizes per process, so every
    # run reshuffled the page and produced a diff of pure churn.
    for year_pubs in pubs_by_year.values():
        year_pubs.sort(
            key=lambda p: (p.get('month', 0), p.get('day', 0), int(p['pmid'] or 0)),
            reverse=True
        )

    # Read the current file to preserve the header
    if PUBLICATIONS_FILE.exists():
        content = PUBLICATIONS_FILE.read_text()
        # Find where the publication list starts (after the "---" separator)
        if '\n---\n' in content:
            header_parts = content.split('\n---\n', 2)
            if len(header_parts) >= 2:
                header_content = header_parts[0] + '\n---\n' + header_parts[1].split('\n<ul')[0]
                # Remove any existing "Last updated" lines to prevent duplicates
                lines = header_content.split('\n')
                lines = [line for line in lines if not line.strip().startswith('*Last updated:')]
                header_content = '\n'.join(lines).rstrip() + '\n'
            else:
                header_content = create_default_header()
        else:
            header_content = create_default_header()
    else:
        header_content = create_default_header()

    # Build the publications list section
    current_date = datetime.now().strftime("%B %d, %Y")
    total_pubs = sum(len(pubs) for pubs in pubs_by_year.values())
    preprint_count = sum(1 for pubs in pubs_by_year.values()
                         for pub in pubs if pub['is_preprint'])
    reviewed_count = total_pubs - preprint_count
    preprint_label = 'preprint' if preprint_count == 1 else 'preprints'

    pubs_section = f"""
*Last updated: {current_date} — {reviewed_count} peer-reviewed publications and {preprint_count} {preprint_label} awaiting peer review*

---

<ul class="publication-list">

"""

    # Add publications grouped by year
    for year in sorted_years:
        # Add year publications
        for pub in pubs_by_year[year]:
            pubs_section += '<li class="publication-item">\n'
            pubs_section += f'  <div class="publication-title">{pub["title"]}</div>\n'
            pubs_section += f'  <div class="publication-authors">{pub["authors"]}</div>\n'

            # Journal and year. Preprints are marked inline rather than with a
            # styled badge so the distinction survives in plain text and screen
            # readers without needing a CSS change.
            journal_info = pub['journal']
            if pub['year']:
                journal_info += f', {pub["year"]}'
            if pub['is_preprint']:
                journal_info += ' (preprint, not peer reviewed)'
            pubs_section += f'  <div class="publication-journal">{journal_info}</div>\n'

            # Links
            pubs_section += '  <div class="publication-links">\n'
            pubs_section += f'    <a href="https://pubmed.ncbi.nlm.nih.gov/{pub["pmid"]}/"><span class="visually-hidden">{pub["title"]}: </span>PubMed</a>\n'
            if pub['doi']:
                pubs_section += f'    <a href="https://doi.org/{pub["doi"]}"><span class="visually-hidden">{pub["title"]}: </span>DOI</a>\n'
            pubs_section += '  </div>\n'
            pubs_section += '</li>\n\n'

    pubs_section += """</ul>

---

*This list is updated periodically. For the most current list, please also see [PubMed](https://pubmed.ncbi.nlm.nih.gov/?term=TaMADOR) and individual research group pages.*
"""

    # Combine and write
    new_content = header_content + pubs_section
    PUBLICATIONS_FILE.write_text(new_content)
    print(f"Updated {PUBLICATIONS_FILE} with {total_pubs} publications across {len(sorted_years)} years")
    return True


def create_default_header():
    """Create default header for publications.md if it doesn't exist."""
    return """---
layout: default
title: Publications
permalink: /publications/
---

# Publications

Publications from the TaMADOR consortium supported by:
- U01 DK137097 (University of Washington)
- U01 DK137113 (Pacific Northwest National Laboratories)
- U01 DK124020 (Pacific Northwest National Laboratories)
- U01 DK124019 (Cedars-Sinai Medical Center)

## Publication Metrics

![Publications per Year]({{ '/assets/images/publication-metrics.png' | relative_url }})

---
"""


def generate_publications_plot(publications):
    """
    Generate a bar plot showing publications per year.
    """
    if not publications:
        print("No publications for plot generation")
        return False

    # Count peer-reviewed publications and preprints separately per year
    year_counts = {}
    for pub in publications:
        year = pub.get('year', '')
        if year:
            try:
                year = int(year)
            except ValueError:
                continue
            counts = year_counts.setdefault(year, {'reviewed': 0, 'preprint': 0})
            counts['preprint' if pub['is_preprint'] else 'reviewed'] += 1

    if not year_counts:
        print("No year data available for plot")
        return False

    # Create the plot
    fig, ax = plt.subplots(figsize=(8, 4))

    years = sorted(year_counts.keys())
    reviewed = [year_counts[y]['reviewed'] for y in years]
    preprints = [year_counts[y]['preprint'] for y in years]
    counts = [r + p for r, p in zip(reviewed, preprints)]

    # Two-series categorical palette, validated for colour-vision deficiency
    # separation against a light surface. REVIEWED_COLOR is the website's
    # primary blue nudged up in chroma so it does not read as gray.
    REVIEWED_COLOR = '#1a5490'
    PREPRINT_COLOR = '#d99a2b'

    # White edges give the 2px surface gap that keeps stacked segments distinct
    ax.bar(years, reviewed, color=REVIEWED_COLOR, edgecolor='white', linewidth=1.5,
           label='Peer reviewed')
    ax.bar(years, preprints, bottom=reviewed, color=PREPRINT_COLOR,
           edgecolor='white', linewidth=1.5, label='Preprint')
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Publications', fontsize=12, fontweight='bold')
    ax.set_title('TaMADOR Publications per Year', fontsize=14, fontweight='bold')
    ax.legend(frameon=False, fontsize=10)

    # Set x-axis to show all years
    if len(years) > 0:
        ax.set_xlim(min(years) - 0.5, max(years) + 0.5)
        ax.set_xticks(years)

    # Add gridlines for better readability
    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)

    # Ensure y-axis starts at 0
    ax.set_ylim(0, max(counts) * 1.15 if counts else 10)

    # Value labels on top of each bar. Years that include a preprint show the
    # split ('19 + 1', peer reviewed then preprint, matching the stacking order)
    # because a single number over a stacked bar is ambiguous about whether it
    # means the total or only the peer-reviewed segment.
    for year, reviewed_count, preprint_count in zip(years, reviewed, preprints):
        label = (f'{reviewed_count} + {preprint_count}' if preprint_count
                 else str(reviewed_count))
        ax.text(year, reviewed_count + preprint_count, label,
                ha='center', va='bottom', fontweight='bold')

    # Adjust layout
    plt.tight_layout()

    # Ensure output directory exists
    PLOT_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Save the plot
    plt.savefig(PLOT_OUTPUT_FILE, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    print(f"Generated publications plot: {PLOT_OUTPUT_FILE}")
    return True


def main():
    print("=" * 60)
    print("TaMADOR Publication Fetcher")
    print("=" * 60)
    print()
    print(f"Searching PubMed for grants:")
    for grant in GRANT_NUMBERS:
        print(f"  - {grant}")
    print()
    print(f"Query: {PUBMED_SEARCH_TERM}")
    print()

    # Search PubMed
    pmids = search_pubmed(PUBMED_SEARCH_TERM, MAX_RESULTS)
    print(f"Found {len(pmids)} publications from grant search")

    # Add additional PMIDs (avoid duplicates)
    pmids_set = set(pmids)
    genuinely_new = sorted(set(ADDITIONAL_PMIDS) - pmids_set)
    pmids_set.update(ADDITIONAL_PMIDS)

    # Sorted, not list(set), so the fetch order is stable across runs
    pmids = sorted(pmids_set)

    if ADDITIONAL_PMIDS:
        already_found = len(ADDITIONAL_PMIDS) - len(genuinely_new)
        print(f"Additional PMIDs: {len(genuinely_new)} added, "
              f"{already_found} already found by grant search")
        for pmid in genuinely_new:
            print(f"  + {pmid}")
    print(f"Total: {len(pmids)} publications")

    if not pmids:
        print("No publications found")
        return

    # Fetch publication details
    print("Fetching publication details...")
    publications = fetch_publication_details(pmids)
    print(f"Fetched details for {len(publications)} publications")
    print()

    # Collapse preprint/published duplicates so no paper is counted twice
    print("Resolving preprints...")
    publications = resolve_preprints(publications)
    remaining_preprints = sum(1 for pub in publications if pub['is_preprint'])
    print(f"{len(publications)} distinct papers: "
          f"{len(publications) - remaining_preprints} peer reviewed, "
          f"{remaining_preprints} awaiting peer review")
    print()

    # Update publications file
    print("Updating publications.md...")
    update_publications_file(publications)
    print()

    # Generate plot
    print("Generating publications plot...")
    generate_publications_plot(publications)
    print()

    print("=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == '__main__':
    main()
