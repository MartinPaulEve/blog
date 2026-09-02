---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2012/01/23/ive-gone-to-ipv6
categories:
- Technology
comments: []
date: 2012-01-23 15:28:50 +0100
date_gmt: 2012-01-23 15:28:50 +0100
doi: https://doi.org/10.59348/xrz0p-4p591
roguescholar: https://rogue-scholar.org/records/a6t7w-n8n53
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7miyfjoq2o
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Technology
- IPv6
title: I've gone to IPv6
wordpress_id: 1864
wordpress_url: https://www.martineve.com/2012/01/23/ive-gone-to-ipv6/
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7miyfjoq2o"
kcworks: https://works.hcommons.org/records/3bpss-x5r31
---

<p>2012 has been designated <a href="http://www.worldipv6launch.org/">the year of IPv6 launch</a> and, to do my part, I have tweaked my infrastructure to ensure full, and future-guaranteed, IPv6 connectivity.</p>
<p>The following domains now support connections via IPv6:</p>
<p><a href="http://www.martineve.com">martineve.com</a><br />
<a href="http://www.pynchon.net">pynchon.net</a><br />
<a href="http://www.excursions-journal.org.uk">excursions-journal.org.uk</a><br />
<a href="http://www.2bitpie.net">2bitpie.net</a></p>
<p>DNS may still be propogating, but all should be 100% within 48 hours.</p>
<p>In order to test this, and to enable permanent IPv6 connectivity to my home, I had to configure a 6-in-4 tunnel to my server box using OpenVPN and <a href="https://www.zagbot.com/openvpn_ipv6_tunnel.html">the instructions at zagbot</a>. A note to anybody else trying this. The instructions imply that it might work for you without the "sudo /sbin/ip -6 neigh add proxy ${BASERANGE}:${V6NET}::2 dev eth0" line. For me, it did not. Before panicking that things aren't working, try it with that line!</p>
<p><img src="https://www.martineve.com/wp-content/uploads/2012/01/vint-1024x1024.jpg" alt="Vint Cerf" title="Vint Cerf" style="width:750px;" class="alignnone size-large wp-image-1866" /></p>
<p><i>Featured image by <a href="http://www.flickr.com/photos/mneylon/">blacknight</a> under a CC-BY license.</i></p>