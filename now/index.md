---
layout: page
title: Now
excerpt: "What Martin Paul Eve is doing now: current writing, thinking, learning, and listening, drawn from the site's live streams."
og_card_image: mpe.png
pdf: false
comments: false
---

This is a [now page](https://nownownow.com/about): a snapshot of what
I'm up to at the moment, assembled from this site's streams every time
it rebuilds — so it is current as of {{ site.time | date: "%-d %B %Y" }}.

{% comment %}
  Hand-written sections go anywhere in this file as ordinary Markdown —
  right here is a good spot (current projects, reading, life news).
  The Liquid-tagged blocks below are the automated sections; leave
  those intact and write around them.
{% endcomment %}

## Writing

The most recent long-form pieces:

<ul>
{% for post in site.posts limit: 3 %}
<li><a href="{{ post.url }}">{{ post.title }}</a> <small>({{ post.date | date: "%-d %B %Y" }})</small></li>
{% endfor %}
</ul>

## Thinking

{% assign thought = site.data.thoughts | first %}
{% if thought %}
The latest [short thought](/thoughts/):

<blockquote>
<p>{{ thought.text | linkify_urls }}</p>
<p><small><a href="{{ thought.id | thought_month_url }}#t{{ thought.id }}">{{ thought.date | date: "%-d %B %Y, %H:%M" }}</a></small></p>
</blockquote>
{% endif %}

## Learning

{% assign til = site.data.thoughts | til_entries | first %}
{% if til %}
The most recent entry from [Today I Learned](/til/):

<blockquote>
<p>{{ til.text | linkify_urls }}</p>
<p><small><a href="/til/#t{{ til.id }}">{{ til.date | date: "%-d %B %Y" }}</a></small></p>
</blockquote>
{% else %}
See [Today I Learned](/til/) for the small things I pick up along the way.
{% endif %}

## Listening

{% if site.data.lastfm %}
{% if site.data.lastfm.last_played %}{% if site.data.lastfm.last_played.now_playing %}Right now:{% else %}Most recently:{% endif %} *{{ site.data.lastfm.last_played.track }}* by {{ site.data.lastfm.last_played.artist }}.{% endif %}
{% if site.data.lastfm.top_artist %}The band I have played most lately is [{{ site.data.lastfm.top_artist.artist }}]({{ site.data.lastfm.top_artist.url }}).{% endif %}
[Scrobbled on Last.fm]({{ site.data.lastfm.url }}).
{% else %}
Listening stats appear here once the site has Last.fm data.
{% endif %}

---

For who I am and what I do more permanently, see [about](/about/),
[accounts](/accounts/), or the [CV](/cv) <i class="fa-solid fa-file-pdf" aria-hidden="true"></i><span class="sr-only">(PDF)</span>.
