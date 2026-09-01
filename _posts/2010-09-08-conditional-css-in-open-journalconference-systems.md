---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/09/08/conditional-css-in-open-journalconference-systems
categories:
- Publishing Technology
comments: []
date: 2010-09-08 10:20:06 +0200
date_gmt: 2010-09-08 10:20:06 +0200
doi: https://doi.org/10.59348/8erd9-1dk39
roguescholar: https://rogue-scholar.org/records/n10cv-3eb71
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mlrxicm2i
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- OJS
- OCS
- Open Access
- CSS
title: Conditional CSS in Open Journal/Conference Systems
wordpress_id: 6
wordpress_url: http://new.martineve.com/?p=6
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mlrxicm2i"
---

<p>    One of the most tedious aspects of establishing a uniquely themed Open Journal or Open Conference Systems site is in getting the CSS to work as you would like. While there are varying schools of thought regarding best practice for implementing cross browser compatibility, my chosen methodology is to write compliant XHTML 1.0 Transitional markup, followed by valid CSS 2 that should do the job, followed by the moderate contamination of conditional comments to include style sheets for Internet Explorer 6 and 7 where compliance isn't achieved.
OJS and OCS provide many ways of getting raw markup into the document but, to the best of my knowledge, no way of injecting into the head field.
Anyway, here's the solution (simple, I know, but might save someone looking for a longer period). Simple replace the closing head tag with the following inside templates/common/header.tpl
<p> &lt;!--[if lte IE 6]&gt; &lt;link href="{$baseUrl}/styles/ie6.css" rel="stylesheet" type="text/css"&gt; &lt;![endif]--&gt; </p>
<p> &lt;!--[if IE 7]&gt; &lt;link href="{$baseUrl}/styles/ie7.css" rel="stylesheet" type="text/css"&gt; &lt;![endif]--&gt; </p>
<p>
You can then edit ie6.css and ie7.css which are conditionally included. Don't forget to add !important tags to any overrides which don't give a higher level of specificity than set in earlier sheets.</p>