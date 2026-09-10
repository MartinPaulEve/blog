---
layout: page
title: Short Thoughts
excerpt: "Short thoughts — micro-posts syndicated to Bluesky and Mastodon."
og_card_image: mpe.png
regenerate: true
---

<link rel="stylesheet" href="/assets/css/thoughts.css?v={{ site.time | date: '%s' }}">

<div class="thoughts-list h-feed">
{% for thought in site.data.thoughts %}
    <article class="thought-entry h-entry" id="t{{ thought.id }}">
        <p class="thought-text e-content">{{ thought.text | linkify_urls }}</p>
        {% if thought.images %}
        <div class="thought-images">
            {% for image in thought.images %}
            <img src="{{ image.src }}" alt="{{ image.alt | escape }}" loading="lazy">
            {% endfor %}
        </div>
        {% endif %}
        <footer class="thought-meta">
            <a class="u-url" href="#t{{ thought.id }}">
                <time class="dt-published" datetime="{{ thought.date }}">{{ thought.date | date: "%-d %B %Y, %H:%M" }}</time>
            </a>
            {% if thought.bluesky %}&middot; <a href="{{ thought.bluesky }}" class="u-syndication" rel="syndication">Bluesky</a>{% endif %}
            {% if thought.mastodon %}&middot; <a href="{{ thought.mastodon }}" class="u-syndication" rel="syndication">Mastodon</a>{% endif %}
        </footer>
    </article>
{% else %}
    <p>No thoughts yet.</p>
{% endfor %}
</div>
