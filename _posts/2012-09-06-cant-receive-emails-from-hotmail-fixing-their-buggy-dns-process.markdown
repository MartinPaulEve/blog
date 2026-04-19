---
layout: post
status: publish
published: true
title: ! 'Can''t receive emails from Hotmail: fixing their buggy DNS process'
wordpress_id: 2383
wordpress_url: https://www.martineve.com/?p=2383
date: !binary |-
  MjAxMi0wOS0wNiAxMTo1MjozMSArMDIwMA==
date_gmt: !binary |-
  MjAxMi0wOS0wNiAxMDo1MjozMSArMDIwMA==
categories:
- Technology
tags:
- DNS
- Microsoft
- Google Apps
comments: []
doi: "https://doi.org/10.59348/mmy5f-dgh59"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2012/09/06/cant-receive-emails-from-hotmail-fixing-their-buggy-dns-process"
---
<p>I run Google Apps for Domains to handle my email. Recently, a friend was having trouble emailing me. I asked her to send me the source of the message. In there, I found this:</p>
<blockquote><p>Diagnostic-Code: smtp;554 5.7.1 <martin@martineve.com>: Relay access denied</p></blockquote>
<p>My A records point to my server.<br />
My MX records point to Google Apps.</p>
<p>I know that the Google Apps servers wouldn't refuse that request, so what's going on?</p>
<p>It turns out that Hotmail, in its infinite wisdom, <a href="http://www.dorianmoore.com/works/6318/working-round-hotmail-live-msn-email-failing-to-deliver-email">decides that it would be better to query the A record</a> and see if there's an SMTP server running on Port 25 there. If there is, it <b>ignores the MX records</b> and tries to relay through that server. So that'll be complete disregard for RFCs <a href="https://tools.ietf.org/html/rfc974">974</a> and <a href="https://www.ietf.org/rfc/rfc2821.txt">2821</a> then. Humph.</p>
<p>So, the solution is either to use iptables to drop packets from Hotmail servers or, as I have now done (and meant to do from the start(!)), to move postfix to listen only on localhost.</p>
<blockquote><p>inet_interfaces = localhost</p></blockquote>
<p>That ought to do it.</p>





