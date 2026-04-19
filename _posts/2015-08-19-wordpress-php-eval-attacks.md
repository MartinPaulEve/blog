---
layout: post
image: 
    feature: geek.png
title: Wordpress php eval attacks
categories: [wordpress]
tags: [wordpress]
published: True
doi: "https://doi.org/10.59348/4wvv5-fe614"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2015/08/19/wordpress-php-eval-attacks"
---

Sigh. More hacking attempts and seems someone did manage to inject a php eval attack into one of my Wordpress installs.

It's not a silver bullet magic fix, because the database and filesystems can also be compromised, but for those who'd like a quick shell command to clean this type of attack from the PHP files, at least:

    find ./ -name '*.php' -type f -exec sed -i -e '/php eval/ { d; }' {} \;




