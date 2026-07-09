---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2014/06/02/update-grubos-prober-not-detecting-windows-7
categories:
- Technology
- Linux
comments: []
date: 2014-06-02 13:37:23 +0200
date_gmt: 2014-06-02 12:37:23 +0200
doi: https://doi.org/10.59348/x5c96-yp709
image:
  feature: geek.png
layout: post
ogImage: geek.png
published: true
status: publish
tags:
- Linux
title: update-grub/os-prober not detecting Windows 7
wordpress_id: 3125
wordpress_url: https://www.martineve.com/?p=3125
---

<p>Note to self/anybody else it might help: if you have disks with previous dmraid headers (potentially corrupt etc.), you need to remove the dmraid package before grub can find a Windows partition that resides on those disks. This is because the dmraid package is attempting to map the drives to /dev/mapper locations.</p>