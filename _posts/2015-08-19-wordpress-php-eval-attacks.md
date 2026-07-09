---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2015/08/19/wordpress-php-eval-attacks
categories:
- wordpress
date: 2015-08-19
doi: https://doi.org/10.59348/4wvv5-fe614
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
tags:
- wordpress
title: Wordpress php eval attacks
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mccvbrj2f"
---

Sigh. More hacking attempts and seems someone did manage to inject a php eval attack into one of my Wordpress installs.

It's not a silver bullet magic fix, because the database and filesystems can also be compromised, but for those who'd like a quick shell command to clean this type of attack from the PHP files, at least:

    find ./ -name '*.php' -type f -exec sed -i -e '/php eval/ { d; }' {} \;