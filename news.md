---
layout: default
title: News
permalink: /news/
---

# News & Announcements

<p><a href="{{ '/feed.xml' | relative_url }}">Subscribe via RSS</a></p>

---

<ul class="news-list">
{% for post in site.posts %}
<li class="news-item">
  <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
  <div class="news-date">{{ post.date | date: "%B %-d, %Y" }}</div>
  <p class="news-excerpt">{{ post.excerpt | strip_html }}</p>
  <p><a href="{{ post.url | relative_url }}">Read more &rarr;</a></p>
</li>
{% endfor %}
</ul>

{% if site.posts.size == 0 %}
<p>No news posts yet. Check back soon!</p>
{% endif %}
