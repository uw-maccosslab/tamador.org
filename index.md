---
layout: default
title: TaMADOR - Targeted Mass Spectrometry Assays for Diabetes and Obesity Research
---

<div class="hero">
  <h1>Welcome to TaMADOR</h1>
  <p>Two NIDDK programs, one focused on Type 1 Diabetes and one focused on Obesity, funded research groups with the goal of developing and disseminating targeted mass spectrometry assays for the diagnosis and monitoring of Type 1 Diabetes and Obesity. While the funding sources are separate, we felt there were obvious synergies in these efforts and formed TaMADOR with the goal of leveraging each other's capabilities and strengths.</p>
</div>

<div class="rfa-links">
  <h3>NIH Funding Announcements</h3>
  <ul>
    <li><a href="https://grants.nih.gov/grants/guide/rfa-files/RFA-DK-17-019.html">Type 1 Diabetes RFA (RFA-DK-17-019)</a></li>
    <li><a href="https://grants.nih.gov/grants/guide/rfa-files/RFA-DK-19-001.html">Obesity RFA (RFA-DK-19-001)</a></li>
    <li><a href="https://grants.nih.gov/grants/guide/rfa-files/RFA-DK-21-031.html">Type 1 Diabetes Continuation (RFA-DK-21-031)</a></li>
  </ul>
</div>

<div class="groups-section">
  <h2>Type 1 Diabetes Assays</h2>
  <div class="groups-grid">
    <div class="group-card">
      <h3><a href="https://panoramaweb.org/TAMADOR/UW%20Medicine%20-%20NIDDK%20U01%20Diabetes%20Assays/project-begin.view">University of Washington</a></h3>
      <p>Quantifying Proteins in Plasma to Democratize Personalized Medicine for Patients with Type 1 Diabetes</p>
      <p><strong>PIs:</strong> Andrew Hoofnagle, Michael MacCoss</p>
    </div>
    <div class="group-card">
      <h3><a href="https://panoramaweb.org/TAMADOR/project-begin.view">PNNL & University at Buffalo</a></h3>
      <p>Robust Mass Spectrometric Protein/Peptide Assays for Type 1 Diabetes Clinical Applications</p>
      <p><strong>PIs:</strong> Jun Qu, Wei-Jun Qian</p>
    </div>
  </div>
</div>

<div class="groups-section">
  <h2>Obesity Assays</h2>
  <div class="groups-grid">
    <div class="group-card">
      <h3><a href="https://panoramaweb.org/TAMADOR/Cedars-Sinai%20Group/project-begin.view">Cedars-Sinai Medical Center</a></h3>
      <p>Design and Validation of Easy-to-Adopt Mass Spectrometry Assays of Importance to Obesity</p>
      <p><strong>PI:</strong> Jennifer Van Eyk</p>
    </div>
    <div class="group-card">
      <h3><a href="https://panoramaweb.org/TAMADOR/PNNL%20Group/project-begin.view">Pacific Northwest National Laboratory</a></h3>
      <p>Multiplex Mass Spectrometric Protein Assays for Precise Monitoring of the Pathophysiology of Obesity</p>
      <p><strong>PI:</strong> Wei-Jun Qian</p>
    </div>
  </div>
</div>

<div class="partners-section">
  <h2>Participating Institutions</h2>
  <div class="partners-grid">
    <div class="partner-logo">
      <img src="{{ '/assets/images/logos/UWSOMVert_fullColor_RGB.png' | relative_url }}" alt="University of Washington" onerror="this.parentElement.innerHTML='<div class=\'logo-placeholder\'>University of Washington</div>'">
    </div>
    <div class="partner-logo">
      <img src="{{ '/assets/images/logos/PNNL_CENTER_FullColorSMALL.jpg' | relative_url }}" alt="Pacific Northwest National Laboratory" onerror="this.parentElement.innerHTML='<div class=\'logo-placeholder\'>Pacific Northwest National Laboratory</div>'">
    </div>
    <div class="partner-logo">
      <img src="{{ '/assets/images/logos/Cedars-Sinai.png' | relative_url }}" alt="Cedars-Sinai Medical Center" onerror="this.parentElement.innerHTML='<div class=\'logo-placeholder\'>Cedars-Sinai Medical Center</div>'">
    </div>
    <div class="partner-logo">
      <img src="{{ '/assets/images/logos/University_at_Buffalo_logo.png' | relative_url }}" alt="University at Buffalo" onerror="this.parentElement.innerHTML='<div class=\'logo-placeholder\'>University at Buffalo</div>'">
    </div>
  </div>
</div>

<div class="news-section">
  <div class="section-header">
    <h2>News & Announcements</h2>
    <a href="{{ '/news' | relative_url }}">View all &rarr;</a>
  </div>
  <ul class="news-list">
    {% for post in site.posts limit:5 %}
    <li class="news-item">
      <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
      <div class="news-date">{{ post.date | date: "%B %-d, %Y" }}</div>
      <p class="news-excerpt">{{ post.excerpt | strip_html | truncate: 200 }}</p>
    </li>
    {% endfor %}
  </ul>
</div>
