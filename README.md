# TaMADOR Website

Website for the TaMADOR (Targeted Mass Spectrometry Assays for Diabetes and Obesity Research) consortium.

**Live site:** [https://tamador.org](https://tamador.org)
**Repository:** [https://github.com/uw-maccosslab/tamador.org](https://github.com/uw-maccosslab/tamador.org)
**Internal site:** [https://panoramaweb.org/TAMADOR/Internal/project-begin.view](https://panoramaweb.org/TAMADOR/Internal/project-begin.view)

## Overview

This is a Jekyll-based static website hosted on GitHub Pages. The site includes:

- Information about the TaMADOR consortium and participating institutions
- Automatically updated publications list from PubMed (52 publications)
- Publication metrics chart showing publications per year
- Datasets and links to Panorama Public
- Meeting information and archives
- News and announcements (with RSS feed)
- Member login link to the internal Panorama site
- Institution logos (UW, PNNL, Cedars-Sinai, Buffalo)

## Local Development

```bash
# Install dependencies
bundle install

# Run local server
bundle exec jekyll serve
```

Then visit `http://localhost:4000`

## Site Structure

```
├── _config.yml          # Jekyll configuration
├── _layouts/            # Page templates
│   ├── default.html     # Main site layout
│   └── post.html        # News post layout
├── _posts/              # News posts (YYYY-MM-DD-title.md)
├── assets/
│   ├── css/style.css    # Site styles
│   └── images/          # Images and logos
├── index.md             # Homepage
├── publications.md      # Publications page
├── datasets.md          # Datasets page
├── meetings.md          # Meetings page
├── news.md              # News listing page
└── contact.md           # Contact page
```

## Institution Logos

The site displays logos for participating institutions. Place logo files in `assets/images/logos/`:
- `uw-logo.png` - University of Washington
- `pnnl-logo.png` - Pacific Northwest National Laboratory
- `cedars-sinai-logo.png` - Cedars-Sinai Medical Center
- `buffalo-logo.png` - University at Buffalo

See `assets/images/logos/README.md` for detailed requirements. The site will display text placeholders if logo images are not available.

## Adding Content

### News Posts

Create a new file in `_posts/` with the format `YYYY-MM-DD-title.md`:

```markdown
---
layout: post
title: "Your Post Title"
date: 2025-01-15
categories: [news, meetings]
---

Your post content here.
```

### Publications

Edit `publications.md` to add new publications. Follow the existing format.

### Datasets

Edit `datasets.md` to add new dataset links.

## Custom Domain Setup

The site uses the custom domain `tamador.org`. DNS is configured to point to GitHub Pages.

The `CNAME` file contains: `tamador.org`

## Publication Automation

The site automatically fetches and updates publications from PubMed that credit the TaMADOR grants.

### Running the Publication Script

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the publication fetcher
python scripts/fetch_publications.py

# Deactivate when done
deactivate
```

**What it does:**
- Queries PubMed for papers crediting grants: U01 DK137097, U01 DK137113, U01 DK124020, U01 DK124019
- Updates `publications.md` with the complete publication list
- Generates `assets/images/publication-metrics.png` chart showing publications per year

**Setup:**
```bash
# Create virtual environment
python3 -m venv .venv

# Install dependencies
source .venv/bin/activate
pip install -r requirements.txt
```

See [scripts/README.md](scripts/README.md) and [scripts/USAGE.md](scripts/USAGE.md) for more details on automation options (cron jobs, GitHub Actions).

## Deployment

The site is deployed to GitHub Pages with a custom domain `tamador.org`.

### DNS Configuration

The domain is configured on GoDaddy with the following DNS records:

**A Records** (4 entries pointing to GitHub Pages):
- `@` → 185.199.108.153
- `@` → 185.199.109.153
- `@` → 185.199.110.153
- `@` → 185.199.111.153

**CNAME Record**:
- `www` → uw-maccosslab.github.io

### GitHub Pages Setup

1. Repository Settings → Pages
2. Source: Deploy from `main` branch, `/ (root)` folder
3. Custom domain: `tamador.org`
4. Enforce HTTPS: ✓ Enabled

### Deployment Process

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment instructions including:
- Step-by-step GoDaddy DNS configuration
- GitHub Pages setup and verification
- Troubleshooting common issues
- DNS propagation verification

## Updating the Site

1. Make changes locally or via GitHub
2. Commit and push to the `main` branch
3. GitHub Pages will automatically rebuild the site (1-2 minutes)
4. Visit https://tamador.org to see changes

**Note:** The CNAME file should not be modified manually - it's managed by GitHub Pages.

## License

CC0-1.0
