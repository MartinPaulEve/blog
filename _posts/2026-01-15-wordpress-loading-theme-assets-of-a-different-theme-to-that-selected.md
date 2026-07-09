---
archive: https://wayback.archive-it.org/22123/20241101171236/https://eve.gd/2026/01/15/wordpress-loading-theme-assets-of-a-different-theme-to-that-selected/
date: 2026-01-15
doi: https://doi.org/10.59348/75w3f-xhg06
image:
  feature: header_geek.png
layout: post
ogImage: images/header_geek.png
title: WordPress loading theme assets of a different theme to that selected
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lvas6us2h"
---

Today's tech anomaly was odd. I'm working on a new WordPress theme and obviously WordPress has to load its assets like the CSS file and the JavaScript file. I just added some new code to the home page template and suddenly my CSS was not loading. In fact it was pointing to the next theme in the list, Blockbase, and loading its CSS. Nothing I could do with caching resolved this in the slightest.

So it eventually turns out that if you add really bad code that crashes to a template, WordPress decides that it should not load your theme assets and it should load them from somewhere else. You can almost guarantee that this problem occurs because of crashing code somewhere in a theme.