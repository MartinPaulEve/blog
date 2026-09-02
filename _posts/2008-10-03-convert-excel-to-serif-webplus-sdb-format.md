---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2008/10/03/convert-excel-to-serif-webplus-sdb-format
categories:
- Technology
comments: []
date: 2008-10-03 05:13:06 +0200
date_gmt: 2008-10-03 05:13:06 +0200
doi: https://doi.org/10.59348/qtmkv-77x51
roguescholar: https://rogue-scholar.org/records/d2j1r-kc783
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmnq2342s
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Excel
- Serif Webplus
title: Convert Excel to Serif Webplus SDB format
wordpress_id: 246
wordpress_url: http://pro.grammatic.org/post-convert-excel-to-serif-webplus-sdb-format-56.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmnq2342s"
kcworks: https://works.hcommons.org/records/tymxx-vk906
---

<p>Just sharing something that might be of interest to anyone with a similar problem.</p>
<p>A non-technically minded friend is attempting to use Serif WebPlus to create an E-Commerce site with Paypal integration. The problem is that all his stock is in Excel format which, although Serif claims they can handle, throws an error dialog with the helpful information that the worksheet or database does not have the required fields. There is no indication as to what these fields should be, merely that they are required and not present!</p>
<p>Anyway, I figured I'd have more success with an export to CSV. Nope, exactly the same problem.</p>
<p>Finally, after actually opening an actual "SDB" file in notepad I noticed that the Serif Database file IS a CSV file. The only difference? It comes with quotation marks around each field. Hello, there -> "Hello", "there". Great.</p>