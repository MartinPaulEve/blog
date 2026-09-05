---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2013/09/30/fixing-broken-spellcheck-in-thunderbird-24
categories:
- Technology
comments: []
date: 2013-09-30 11:15:39 +0200
date_gmt: 2013-09-30 10:15:39 +0200
doi: https://doi.org/10.59348/rr88h-fxy46
roguescholar: https://rogue-scholar.org/records/5tv7p-xb725
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mgaijww2e
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- email
- bug
title: Fixing broken spellcheck in Thunderbird 24
wordpress_id: 2901
wordpress_url: https://www.martineve.com/?p=2901
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mgaijww2e"
kcworks: https://works.hcommons.org/records/w8tsv-5ja87
references:
- https://bugzilla.mozilla.org/show_bug.cgi?id=880595#c27 # Mozilla Bugzilla fix for Thunderbird spellcheck bug
---

<p>Quick post to add some Google juice to a problem. If you upgrade to Thunderbird 24 and it no longer underlines your misspelt text in red, go to Tools -> Preferences -> Advanced -> Config Editor and <a href="https://bugzilla.mozilla.org/show_bug.cgi?id=880595#c27">set mail.compose.max_recycled_windows to 0</a>.</p>