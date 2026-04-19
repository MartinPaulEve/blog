---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: update-grub/os-prober not detecting Windows 7
wordpress_id: 3125
wordpress_url: https://www.martineve.com/?p=3125
date: !binary |-
  MjAxNC0wNi0wMiAxMzozNzoyMyArMDIwMA==
date_gmt: !binary |-
  MjAxNC0wNi0wMiAxMjozNzoyMyArMDIwMA==
categories:
- Technology
- Linux
tags:
- Linux
comments: []
doi: "https://doi.org/10.59348/x5c96-yp709"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2014/06/02/update-grubos-prober-not-detecting-windows-7"
---
<p>Note to self/anybody else it might help: if you have disks with previous dmraid headers (potentially corrupt etc.), you need to remove the dmraid package before grub can find a Windows partition that resides on those disks. This is because the dmraid package is attempting to map the drives to /dev/mapper locations.</p>





