---
layout: page
title: Listening
excerpt: "Everything I listen to, scrobbled from Last.fm: a chronological log by month, searchable."
og_card_image: mpe.png
regenerate: true
pdf: false
feed: /listening/feed.atom
---

{% if page.month_plays %}
{% include _listening_page.html %}
{% else %}
<p>Nothing logged yet.</p>
{% endif %}
