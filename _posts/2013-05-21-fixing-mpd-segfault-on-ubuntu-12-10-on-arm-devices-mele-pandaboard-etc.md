---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2013/05/21/fixing-mpd-segfault-on-ubuntu-12-10-on-arm-devices-mele-pandaboard-etc
categories:
- Linux
comments: []
date: 2013-05-21 14:35:14 +0200
date_gmt: 2013-05-21 13:35:14 +0200
doi: https://doi.org/10.59348/426jt-15d79
roguescholar: https://rogue-scholar.org/records/05g9e-5vn29
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mgqn37h2i
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Technology
- mpd
title: Fixing mpd segfault on Ubuntu 12.10 on ARM devices (Mele, Pandaboard etc)
wordpress_id: 2708
wordpress_url: https://www.martineve.com/?p=2708
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mgqn37h2i"
kcworks: https://works.hcommons.org/records/dren2-7n344
---

<p>If you are experiencing crashes when you update your mpd library on Ubuntu 12.10, <a href="https://bugs.launchpad.net/ubuntu/+source/libmad/+bug/989846">the fault is with libmad0</a>.</p>
<p>This can be fixed by installing libmad0 from Debian Wheeze. As root:</p>

{% highlight bash %}
wget http://ftp.us.debian.org/debian/pool/main/libm/libmad/libmad0_0.15.1b-7_armhf.deb
dpkg -i ./libmad0_0.15.1b-7_armhf.deb
{% endhighlight %}

<p>I can confirm that this has fixed my update crashes. When I get to the box itself I'll confirm whether audio playback still works!</p>