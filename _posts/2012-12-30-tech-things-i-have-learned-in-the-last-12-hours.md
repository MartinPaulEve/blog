---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2012/12/30/tech-things-i-have-learned-in-the-last-12-hours
categories:
- Technology
comments: []
date: 2012-12-30 14:10:52 +0100
date_gmt: 2012-12-30 14:10:52 +0100
doi: https://doi.org/10.59348/tz8sx-c4a88
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Linux
- windows
title: Tech things I have learned in the last 12 hours
wordpress_id: 2567
wordpress_url: https://www.martineve.com/?p=2567
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mh6tafx2i"
---

<ol>
<li>It is not worth trying to restore a Windows partition using dd unless you restore it to *exactly* the same offset on the new drive. Even then it might not work. No amount of dicking around with bootrec fixmbr rebuildbcd etc. will solve this.</li>
<li>A fresh Windows install that complains that it is missing the "cd/dvd driver" actually means that there's a problem reading the DVD you've booted from. Do this by USB instead.</li>
<li>There's a cool piece of software called <a href="http://en.congelli.eu/prog_info_winusb.html">WinUSB</a> that will create a Windows installation USB stick for you from inside Linux. You need to download the install media for this, but they're easy to find (and legally distributed).</li>
<li>Windows' partitioner isn't as aggressive as I'd feared, but it will overwrite grub and you need to go back in and use the chroot method to reinstall it.</li>
<li>Bumblebee is great, but <a href="https://www.martineve.com/2012/12/30/using-bumblebee-for-opteron-graphics-on-ubuntu-12-10-on-a-samsung-chronos-7-series-laptop/">hardly works "out of the box"</a></li>
<li>The "discard" flag has to be added to both fstab and crypttab to enable TRIM on a luks device.</li>
</ol>