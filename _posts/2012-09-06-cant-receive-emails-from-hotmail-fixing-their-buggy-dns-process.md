---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2012/09/06/cant-receive-emails-from-hotmail-fixing-their-buggy-dns-process
categories:
- Technology
comments: []
date: 2012-09-06 11:52:31 +0200
date_gmt: 2012-09-06 10:52:31 +0200
doi: https://doi.org/10.59348/mmy5f-dgh59
roguescholar: https://rogue-scholar.org/records/nm5zj-xtx25
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mhsscie2h
layout: post
published: true
status: publish
tags:
- DNS
- Microsoft
- Google Apps
title: 'Can''t receive emails from Hotmail: fixing their buggy DNS process'
wordpress_id: 2383
wordpress_url: https://www.martineve.com/?p=2383
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mhsscie2h"
kcworks: https://works.hcommons.org/records/f1ceh-crt10
references:
- author: Dorian Fraser-Moore
  title: Working round email from Hotmail/Live/MSN failing to be delivered
  type: TechArticle
  url: http://www.dorianmoore.com/works/6318/working-round-hotmail-live-msn-email-failing-to-deliver-email
  isPartOf:
    name: dorian f moore
    type: WebSite
- author: Dr. Craig Partridge
  title: 'RFC 974: Mail routing and the domain system'
  type: TechArticle
  url: https://tools.ietf.org/html/rfc974
  isPartOf:
    name: IETF Datatracker
    type: WebSite
- https://www.ietf.org/rfc/rfc2821.txt # IETF RFC 2821 SMTP protocol specification
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