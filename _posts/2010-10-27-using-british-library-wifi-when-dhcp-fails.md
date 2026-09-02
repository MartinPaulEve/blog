---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/10/27/using-british-library-wifi-when-dhcp-fails
categories:
- Technology
comments:
- author: Tweets that mention Using British Library wifi when DHCP fails | Martin
    Paul Eve -- Topsy.com
  author_email: ''
  author_url: http://topsy.com/www.martineve.com/2010/10/27/using-british-library-wifi-when-dhcp-fails/?utm_source=pingback&amp;utm_campaign=L2
  content: '[...] This post was mentioned on Twitter by Sarah Robins-Hobden, Martin
    Eve. Martin Eve said: New blog post: Using British Library wifi when DHCP fails
    http://www.martineve.com/?p=207 [...]'
  date: 2010-10-27 10:58:43 +0200
  date_gmt: 2010-10-27 10:58:43 +0200
  id: 168
date: 2010-10-27 09:24:20 +0200
date_gmt: 2010-10-27 09:24:20 +0200
doi: https://doi.org/10.59348/r7pf6-7g138
roguescholar: https://rogue-scholar.org/records/x0xpe-dx870
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mlqbos72i
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Technology
- DHCP
title: Using British Library wifi when DHCP fails
wordpress_id: 207
wordpress_url: http://www.martineve.com/?p=207
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mlqbos72i"
kcworks: https://works.hcommons.org/records/438fh-yv646
---

<p>Sometimes, the free wireless service at the British Library goes pear shaped and, if you are accustomed to using it, this can make research quite hard. Occasionally, however the fault is not with the central mechanism but rather with DHCP -- the mechanism that gives your computer an address on their system.</p>
<p>I'm afraid that this is a somewhat technical post, as I don't have time to write a user-friendly (aka. Windows) guide, but to determine if DHCP is at fault (assuming you are using a *nix based system, such as Linux or Mac OS X) you can issue, at a terminal:</p>
<blockquote><p>cat /var/log/syslog | grep DHCP</p></blockquote>
<p>once you've tried, probably unsuccessfully, to connect.</p>
<p>If you see lines like this:</p>
<blockquote><p>Oct 27 10:11:10 allusion dhclient: DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 6<br />
Oct 27 10:11:10 allusion dhclient: DHCPOFFER of 192.168.5.218 from 192.168.4.1<br />
Oct 27 10:11:10 allusion dhclient: DHCPREQUEST of 192.168.5.218 on wlan0 to 255.255.255.255 port 67<br />
Oct 27 10:11:13 allusion dhclient: DHCPREQUEST of 192.168.5.218 on wlan0 to 255.255.255.255 port 67<br />
Oct 27 10:11:21 allusion dhclient: DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 3<br />
Oct 27 10:11:21 allusion dhclient: DHCPOFFER of 192.168.5.218 from 192.168.4.1<br />
Oct 27 10:11:21 allusion dhclient: DHCPREQUEST of 192.168.5.218 on wlan0 to 255.255.255.255 port 67
</p></blockquote>
<p>Then it might be fixable.</p>
<p>Indeed, simply set your wireless adapter to use a static IP, using the address shown in the DHCPOFFER line, a default gateway of 192.168.4.1 and DNS server likewise 192.168.4.1</p>
<p>Tada -- back online.</p>