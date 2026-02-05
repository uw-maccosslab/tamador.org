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

# Build PubMed search query for grant numbers
PUBMED_SEARCH_TERM = ' OR '.join([f'"{grant}"[Grant Number]' for grant in GRANT_NUMBERS])

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

        # Get publication date
        pub_date = article.find('.//PubDate')
        if pub_date is not None:
            year = pub_date.find('Year')
            pub['year'] = year.text if year is not None else ''
        else:
            pub['year'] = ''

        # Get DOI
        doi = None
        for article_id in article.findall('.//ArticleId'):
            if article_id.get('IdType') == 'doi':
                doi = article_id.text
                break
        pub['doi'] = doi

        publications.append(pub)

    return publications


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

    # Read the current file to preserve the header
    if PUBLICATIONS_FILE.exists():
        content = PUBLICATIONS_FILE.read_text()
        # Find where the publication list starts (after the "---" separator)
        if '\n---\n' in content:
            header_parts = content.split('\n---\n', 2)
            if len(header_parts) >= 2:
                header_content = header_parts[0] + '\n---\n' + header_parts[1].split('\n<ul')[0]
            else:
                header_content = create_default_header()
        else:
            header_content = create_default_header()
    else:
        header_content = create_default_header()

    # Build the publications list section
    current_date = datetime.now().strftime("%B %d, %Y")
    total_pubs = sum(len(pubs) for pubs in pubs_by_year.values())

    pubs_section = f"""

*Last updated: {current_date} — {total_pubs} publications*

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

            # Journal and year
            journal_info = pub['journal']
            if pub['year']:
                journal_info += f', {pub["year"]}'
            pubs_section += f'  <div class="publication-journal">{journal_info}</div>\n'

            # Links
            pubs_section += '  <div class="publication-links">\n'
            pubs_section += f'    <a href="https://pubmed.ncbi.nlm.nih.gov/{pub["pmid"]}/">PubMed</a>\n'
            if pub['doi']:
                pubs_section += f'    <a href="https://doi.org/{pub["doi"]}">DOI</a>\n'
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

    # Count publications per year
    year_counts = {}
    for pub in publications:
        year = pub.get('year', '')
        if year:
            try:
                year = int(year)
                year_counts[year] = year_counts.get(year, 0) + 1
            except ValueError:
                pass

    if not year_counts:
        print("No year data available for plot")
        return False

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 5))

    years = sorted(year_counts.keys())
    counts = [year_counts[y] for y in years]

    # Use TaMADOR colors (blue theme matching the website)
    bar_color = '#2c5282'  # Primary blue from website

    ax.bar(years, counts, color=bar_color, edgecolor='white', linewidth=0.5)
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Publications', fontsize=12, fontweight='bold')
    ax.set_title('TaMADOR Publications per Year', fontsize=14, fontweight='bold')

    # Set x-axis to show all years
    if len(years) > 0:
        ax.set_xlim(min(years) - 0.5, max(years) + 0.5)
        ax.set_xticks(years)

    # Add gridlines for better readability
    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)

    # Ensure y-axis starts at 0
    ax.set_ylim(0, max(counts) * 1.15 if counts else 10)

    # Add value labels on top of bars
    for year, count in zip(years, counts):
        ax.text(year, count, str(count), ha='center', va='bottom', fontweight='bold')

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
    print(f"Found {len(pmids)} publications")

    if not pmids:
        print("No publications found")
        return

    # Fetch publication details
    print("Fetching publication details...")
    publications = fetch_publication_details(pmids)
    print(f"Fetched details for {len(publications)} publications")
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
