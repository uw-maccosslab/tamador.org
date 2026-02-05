# TaMADOR Website Deployment Checklist

This document outlines the steps needed to deploy the TaMADOR website and replace the current Panorama page.

## Quick Reference

**Domain:** tamador.org (via GoDaddy)
**GitHub Repo:** https://github.com/uw-maccosslab/tamador.org
**GitHub Pages URL:** https://uw-maccosslab.github.io/tamador.org/
**Internal Site:** https://panoramaweb.org/TAMADOR/Internal/project-begin.view

**Required DNS Records (GoDaddy):**
- 4 × A records: `@` → GitHub IPs (185.199.108-111.153)
- 1 × CNAME record: `www` → `uw-maccosslab.github.io`

## Domain Setup

### 1. Acquire Domain
- [ ] Register `tamador.org` domain (if not already done)
- Recommended registrars: Namecheap, Google Domains, or your institution's preferred provider

### 2. Configure DNS on GoDaddy

#### Step-by-step GoDaddy DNS Configuration:

1. **Log in to GoDaddy**
   - Go to https://www.godaddy.com
   - Sign in to your account
   - Navigate to "My Products"

2. **Access DNS Management**
   - Find your `tamador.org` domain
   - Click the three-dot menu (⋮) next to the domain
   - Select "Manage DNS" or click "DNS" button

3. **Remove Default Records** (if present)
   - Look for existing A records pointing to GoDaddy's parking page
   - Delete any existing A records for `@` (root domain)
   - Delete any existing CNAME records for `www` if they exist

4. **Add GitHub Pages A Records**

   Click "Add" and create **four separate A records**:

   | Type | Name | Value | TTL |
   |------|------|-------|-----|
   | A | @ | 185.199.108.153 | 600 seconds (or default) |
   | A | @ | 185.199.109.153 | 600 seconds (or default) |
   | A | @ | 185.199.110.153 | 600 seconds (or default) |
   | A | @ | 185.199.111.153 | 600 seconds (or default) |

   **Note:** `@` represents your root domain (tamador.org)

5. **Add CNAME Record for www subdomain**

   Click "Add" and create:

   | Type | Name | Value | TTL |
   |------|------|-------|-----|
   | CNAME | www | uw-maccosslab.github.io | 1 Hour (or default) |

   **Important:** Do NOT include a trailing dot after `.io`

6. **Verify Your Records**

   Your final DNS records should look like this:
   ```
   Type    Name    Value                   TTL
   ──────────────────────────────────────────────
   A       @       185.199.108.153         600
   A       @       185.199.109.153         600
   A       @       185.199.110.153         600
   A       @       185.199.111.153         600
   CNAME   www     uw-maccosslab.github.io 3600
   ```

7. **Save Changes**
   - Click "Save" or the changes are auto-saved
   - DNS propagation typically takes 10 minutes to 48 hours

#### Verify DNS Configuration

After saving, you can verify the DNS records are correct using command line tools:

```bash
# Check A records (wait a few minutes after saving)
dig tamador.org +short

# Check CNAME record
dig www.tamador.org +short

# Alternative: use nslookup on Windows
nslookup tamador.org
nslookup www.tamador.org
```

You should see the four GitHub Pages IP addresses for the root domain and `uw-maccosslab.github.io` for the www subdomain.

#### Common GoDaddy Issues:

- **Forwarding:** Make sure domain forwarding is disabled. GitHub Pages handles www redirection.
- **DNSSEC:** If you have DNSSEC enabled, you may need to disable it temporarily during setup.
- **Nameservers:** Ensure nameservers are set to GoDaddy's default nameservers (not external DNS like Cloudflare).

**Note:** DNS propagation can take 24-48 hours, but often completes within 1-2 hours.

### 3. Enable GitHub Pages

#### Configure GitHub Pages:

1. **Navigate to Repository Settings**
   - Go to https://github.com/uw-maccosslab/tamador.org
   - Click "Settings" tab at the top
   - In the left sidebar, click "Pages" (under "Code and automation")

2. **Configure Source**
   - Under "Build and deployment"
   - Source: Select "Deploy from a branch"
   - Branch: Select `main` and folder `/ (root)`
   - Click "Save"

3. **Add Custom Domain**
   - In the "Custom domain" field, enter: `tamador.org`
   - Click "Save"
   - GitHub will create a commit adding/updating the CNAME file
   - Wait for DNS check to complete (green checkmark)

4. **Enable HTTPS** (Important!)
   - **Wait** for DNS to propagate first (check with `dig tamador.org`)
   - Once DNS is working, check the box: "Enforce HTTPS"
   - This may take a few minutes to provision the SSL certificate
   - Your site will be accessible via https://tamador.org

#### Troubleshooting GitHub Pages:

- **"DNS check unsuccessful"**: Wait for DNS propagation (can take hours)
- **HTTPS not working**: Make sure DNS is fully propagated first
- **404 errors**: Check that files are in the correct branch (`main`)
- **Changes not showing**: GitHub Pages build can take 1-2 minutes

#### Check Build Status:

- Go to the "Actions" tab to see build/deployment status
- Green checkmark = successful deployment
- Red X = build failed (check error logs)

## Content Tasks

### 4. Institution Logos ✅ COMPLETE

Logo files have been added to `assets/images/logos/`:
- [x] `UWSOMVert_fullColor_RGB.png` - University of Washington
- [x] `PNNL_CENTER_FullColorSMALL.jpg` - Pacific Northwest National Laboratory
- [x] `Cedars-Sinai.png` - Cedars-Sinai Medical Center
- [x] `University_at_Buffalo_logo.png` - University at Buffalo

All logos are properly configured and will display on the homepage.

### 5. Review Content
- [ ] Review all pages for accuracy
- [ ] Update any outdated information from the AI-generated draft
- [ ] Check all external links (especially Panorama links)
- [ ] Verify Principal Investigator names and affiliations
- [ ] Add any missing recent publications or meetings

### 6. Test Member Login
- [ ] Test the "Members" link: https://panoramaweb.org/TAMADOR/Internal/project-begin.view
- [ ] Verify it requires proper authentication
- [ ] Ensure authorized members can access

## Pre-Launch

### 7. Local Testing
```bash
# Install dependencies
bundle install

# Run locally
bundle exec jekyll serve

# Test at http://localhost:4000
```

**Test checklist:**
- [ ] All pages load correctly
- [ ] Navigation works (including Members link)
- [ ] Responsive design works on mobile
- [ ] Links work (internal and external)
- [ ] Logo placeholders display gracefully
- [ ] News posts display correctly

### 8. Browser Testing
Test on multiple browsers:
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari
- [ ] Mobile browsers (iOS Safari, Chrome Android)

## Launch

### 9. Deploy to GitHub Pages
```bash
git add .
git commit -m "Initial TaMADOR website launch"
git push origin main
```

GitHub Pages will automatically build and deploy within 1-2 minutes.

### 10. Verify Live Site
- [ ] Visit https://tamador.org (after DNS propagation)
- [ ] Check HTTPS works
- [ ] Test all functionality
- [ ] Check Google Analytics (if configured)

## Post-Launch

### 11. Update References
- [ ] Add link from Panorama main page to new tamador.org site
- [ ] Notify consortium members of new site
- [ ] Update any external references to old Panorama URL

### 12. SEO & Discoverability
- [ ] Submit sitemap to Google Search Console
- [ ] Verify meta descriptions are appropriate
- [ ] Check that publications are indexed

## Current Status

✅ **Completed:**
- Site structure and design
- All main pages (Home, Publications, Datasets, Meetings, News, Contact)
- Member login link integration
- Responsive mobile design
- Institution logos (UW, PNNL, Cedars-Sinai, Buffalo)
- News/blog functionality with all 8 announcements from Panorama
- CNAME file configured for tamador.org

⏳ **Pending:**
- Domain registration from GoDaddy (if not already done)
- DNS configuration on GoDaddy
- Enable GitHub Pages with custom domain
- Final content review
- Launch!

## Support

For technical issues with Jekyll or GitHub Pages:
- GitHub Pages Docs: https://docs.github.com/pages
- Jekyll Docs: https://jekyllrb.com/docs/

For content questions, contact the TaMADOR consortium leadership.
