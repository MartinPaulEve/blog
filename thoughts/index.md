---
layout: page
title: Short Thoughts
excerpt: "Short thoughts — micro-posts syndicated to Bluesky and Mastodon."
og_card_image: mpe.png
regenerate: true
pdf: false
---

<link rel="stylesheet" href="/assets/css/thoughts.css?v={{ site.time | date: '%s' }}">

{% assign months = site.data.thoughts | group_by_exp: "thought", "thought.date | slice: 0, 7" %}
{% if months == empty %}
<p>No thoughts yet.</p>
{% else %}
<div class="thoughts-search">
    <input type="search" id="thought-search" placeholder="Search thoughts…" aria-label="Search thoughts" autocomplete="off">
    <p class="thoughts-search-count" id="thought-search-count" hidden></p>
</div>

<nav class="thoughts-months" aria-label="Thoughts by month">
{% for month in months %}    <a href="#m{{ month.name }}">{{ month.name }}</a>{% unless forloop.last %} <span class="thoughts-months-sep" aria-hidden="true">|</span>{% endunless %}
{% endfor %}</nav>

<div class="thoughts-list h-feed">
{% for month in months %}
    <section class="thoughts-month" id="m{{ month.name }}">
        {% assign first = month.items | first %}
        <h2 class="thoughts-month-title">{{ first.date | date: "%B %Y" }}</h2>
        {% for thought in month.items %}
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
                {% if thought.twitter %}&middot; <a href="{{ thought.twitter }}" class="u-syndication" rel="syndication">Twitter</a>{% endif %}
            </footer>
        </article>
        {% endfor %}
    </section>
{% endfor %}
</div>

<script src="/assets/js/thoughts-search.js?v={{ site.time | date: '%s' }}" defer></script>
{% endif %}
