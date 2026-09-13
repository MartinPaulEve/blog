---
layout: page
title: Now
excerpt: "What Martin Paul Eve is doing now: current writing, thinking, learning, and listening, drawn from the site's live streams."
og_card_image: mpe.png
pdf: false
comments: false
---

This is a [now page](https://nownownow.com/about): a snapshot of whatI'm up to at the moment, assembled from this site's streams every time it rebuilds — so it is current as of {{ site.time | date: "%-d %B %Y" }}.

## Knowledge Commons

I am currently working on upgrading BuddyPress across our networks. This is quite a substantial task because our plugins hook to a specific version of this.

I am also onboarding a set of new institutions who particularly want to use our KC Works repository. This is satisfying work, reaching out to libraries.

## Research

In my research professor role, I am currently writing a book for the MIT Press about the dark web. 

I am also writing a somewhat more secret (for now) book about contemporary healthcare and its embroilment in AI technologies.

## Writing

The most recent long-form pieces:

<ul>
{% for post in site.posts limit: 3 %}
<li><a href="{{ post.url }}">{{ post.title }}</a> <small>({{ post.date | date: "%-d %B %Y" }})</small></li>
{% endfor %}
</ul>

## Short Thoughts

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

For who I am and what I do more permanently, see [about](/about/), [accounts](/accounts/), or my [CV](/cv) <i class="fa-solid fa-file-pdf" aria-hidden="true"></i><span class="sr-only">(PDF)</span>.