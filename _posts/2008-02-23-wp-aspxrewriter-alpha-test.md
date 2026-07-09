---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2008/02/23/wp-aspxrewriter-alpha-test
categories:
- Technology
- .NET
comments: []
date: 2008-02-23 21:40:53 +0100
date_gmt: 2008-02-23 21:40:53 +0100
doi: https://doi.org/10.59348/ndrzq-c8c09
image:
  feature: geek.png
layout: post
ogImage: geek.png
published: true
status: publish
tags:
- .NET
- C#
- Wordpress
title: wp-aspxrewriter alpha test
wordpress_id: 257
wordpress_url: http://pro.grammatic.org/post-wpaspxrewriter-alpha-test-44.aspx
---

<p>Well, today I deployed an early version of my wp-aspxrewriter component to my personal blog.</p>
<p>This component is an ASP.NET HttpModule in conjunction with a Wordpress plugin and code hack (official patch for the hack submitted at their <a href="http://trac.wordpress.org/ticket/5969">trac</a> site) which allows 100% pretty permalinks under IIS6.</p>
<p>The current mechanism is grim. A request to a non-existent .aspx page invokes the handler. The handler looks through its regex collection and if a match is found it submits an *http request* to the matching url (impersonating all aspects of the user - just like SSImp) and then filters this back to the client. In short, it is a transparent proxy.</p>
<p>Now I *think* that with IIS7's new pipeline functions it might be possible to force a Server.TransferRequest to a .php file and have IIS handle it properly (ie. select a  new handler, be that ISAPI or CGI/FastCGI), but I still need to test this. In the meantime, I have applied for Wordpress hosting for the plugin and am awaiting some response from them. I furthermore would love it if people would browse around on Recourse for Discourse and let me know if anything looks broken.</p>