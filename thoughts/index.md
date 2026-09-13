---
layout: page
title: Short Thoughts
excerpt: "Short thoughts — micro-posts syndicated to Bluesky and Mastodon."
og_card_image: mpe.png
regenerate: true
pdf: false
---

{% if page.month_thoughts %}
{% include _thoughts_page.html %}
{% else %}
<p>No thoughts yet.</p>
{% endif %}
