---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2014/06/02/update-grubos-prober-not-detecting-windows-7
categories:
- Linux
comments: []
date: 2014-06-02 13:37:23 +0200
date_gmt: 2014-06-02 12:37:23 +0200
doi: https://doi.org/10.59348/x5c96-yp709
roguescholar: https://rogue-scholar.org/records/djer9-5mv49
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mf3wcs72o
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Linux
title: update-grub/os-prober not detecting Windows 7
wordpress_id: 3125
wordpress_url: https://www.martineve.com/?p=3125
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mf3wcs72o"
kcworks: https://works.hcommons.org/records/qzms7-h4h79
---

<p>Note to self/anybody else it might help: if you have disks with previous dmraid headers (potentially corrupt etc.), you need to remove the dmraid package before grub can find a Windows partition that resides on those disks. This is because the dmraid package is attempting to map the drives to /dev/mapper locations.</p>