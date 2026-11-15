---
layout: page
title: Activity
excerpt: "Everything on this site in one chronological log: posts, short thoughts, TILs and listening, by month and searchable."
og_card_image: mpe.png
regenerate: true
pdf: false
feed: /activity/feed.atom
---

{% if page.month_entries %}
{% include _activity_page.html %}
{% else %}
<p>Nothing yet.</p>
{% endif %}
