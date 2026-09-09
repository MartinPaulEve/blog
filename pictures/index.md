---
layout: page
og_card_image: mpe.png
title: Images for re-use
categories: []
tags: []
published: True
image:
  feature: header_new.jpg

---
<link href="/assets/css/pictures.css?v={{ site.time | date: '%s' }}" rel="stylesheet" type="text/css">

The below images of me are released under a [Creative Commons Attribution 4.0 International license](https://creativecommons.org/licenses/by/4.0/) and can be re-used anywhere under the terms of that license. Click an image to view the full-size original, or use the download button beneath it. Each card carries a suggested credit line that you can copy with one click.

<div class="pictures-grid">
{% for pic in site.data.pictures %}
<figure class="picture-card">
<a class="picture-preview" href="{{ pic.file }}" title="View the full-size original">
<img src="{{ pic.preview | default: pic.file }}" alt="{{ pic.description | escape }}" loading="lazy">
</a>
<figcaption class="picture-info">
<p class="picture-description">{{ pic.description }}</p>
{% if pic.width %}<p class="picture-meta">{{ pic.file | split: "." | last | upcase }} · {{ pic.width }}×{{ pic.height }} px · {% if pic.filesize >= 1048576 %}{{ pic.filesize | divided_by: 1048576.0 | round: 1 }} MB{% else %}{{ pic.filesize | divided_by: 1024 }} kB{% endif %}</p>{% endif %}
<p class="picture-credit">{{ pic.credit }}</p>
<div class="picture-actions">
<a class="picture-btn picture-btn-primary" href="{{ pic.file }}" download><i class="fa-solid fa-download" aria-hidden="true"></i> Download</a>
<button class="picture-btn picture-btn-secondary picture-copy" type="button" data-credit="{{ pic.credit | escape }}"><i class="fa-solid fa-copy" aria-hidden="true"></i> Copy credit</button>
</div>
</figcaption>
</figure>
{% endfor %}
</div>

<script src="/assets/js/pictures.js?v={{ site.time | date: '%s' }}" defer></script>
