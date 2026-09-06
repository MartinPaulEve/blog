---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/12/13/djiscography-a-django-based-discography-generator
categories:
- Programming
comments: []
date: 2010-12-13 09:57:32 +0100
last_modified_at: 2026-09-06
date_gmt: 2010-12-13 09:57:32 +0100
doi: https://doi.org/10.59348/5yy8f-pmx37
roguescholar: https://rogue-scholar.org/records/fbyzc-p5m35
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mlixeqt2s
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- django
- djiscography
- music
title: 'Djiscography: a Django-based discography generator'
wordpress_id: 466
wordpress_url: http://www.martineve.com/?p=466
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mlixeqt2s"
kcworks: https://works.hcommons.org/records/6yhz9-gbm50
references:
- http://code.google.com/p/djiscography/ # Djiscography Google Code repository
---

<p><a href="http://www.martineve.com/2010/12/13/djiscography-a-django-based-discography-generator/djiscography/" rel="attachment wp-att-467"><img src="http://www.martineve.com/wp-content/uploads/2010/12/djiscography.png" alt="Djiscography logo" title="djiscography" width="300" height="150" class="size-full wp-image-467" /></a></p>
<p>This is a quick post to announce the first code drop of a project I worked on yesterday. It's called Djiscography and it generates nicely formatted javascript hide/show style discography information. It supports track listing, samples, multiple artists, releases and editions.</p>
<p>A live version of the project can be found at: <a href="http://discography.2bitpie.net">http://discography.2bitpie.net</a>.</p>
<p>The current Mercurial repository features an early alpha version -- I'd recommend caching as I have yet to do optimization work and it currently features two iterations over the data; one in the view to move the data into template-iterable dictionaries and one in the template to display the output.</p>
<p>The code can be found at the <a href="http://code.google.com/p/djiscography/">Google Code repository</a>.</p>
<p>P.S. Logos are, evidently, not my strong point.</p>