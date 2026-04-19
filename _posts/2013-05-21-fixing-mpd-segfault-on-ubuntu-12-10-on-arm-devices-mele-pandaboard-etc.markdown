---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Fixing mpd segfault on Ubuntu 12.10 on ARM devices (Mele, Pandaboard etc)
wordpress_id: 2708
wordpress_url: https://www.martineve.com/?p=2708
date: !binary |-
  MjAxMy0wNS0yMSAxNDozNToxNCArMDIwMA==
date_gmt: !binary |-
  MjAxMy0wNS0yMSAxMzozNToxNCArMDIwMA==
categories:
- Technology
- Linux
tags:
- Technology
- mpd
comments: []
doi: "https://doi.org/10.59348/426jt-15d79"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2013/05/21/fixing-mpd-segfault-on-ubuntu-12-10-on-arm-devices-mele-pandaboard-etc"
---
<p>If you are experiencing crashes when you update your mpd library on Ubuntu 12.10, <a href="https://bugs.launchpad.net/ubuntu/+source/libmad/+bug/989846">the fault is with libmad0</a>.</p>
<p>This can be fixed by installing libmad0 from Debian Wheeze. As root:</p>

{% highlight bash %}
wget http://ftp.us.debian.org/debian/pool/main/libm/libmad/libmad0_0.15.1b-7_armhf.deb
dpkg -i ./libmad0_0.15.1b-7_armhf.deb
{% endhighlight %}

<p>I can confirm that this has fixed my update crashes. When I get to the box itself I'll confirm whether audio playback still works!</p>





