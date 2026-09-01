---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2014/07/05/semantically-marking-up-jats-bibliographies-using-metypeset-and-zotero
categories:
- Publishing Technology
- Programming
comments: []
date: 2014-07-05 15:00:41 +0200
date_gmt: 2014-07-05 14:00:41 +0200
doi: https://doi.org/10.59348/g0dg8-3ck26
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- XML
- meTypeset
- JATS
title: Semantically marking up JATS bibliographies using meTypeset and Zotero
wordpress_id: 3157
wordpress_url: https://www.martineve.com/?p=3157
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mey3ahz2n"
---

<p>A couple of weeks ago I wrote about the <a href="https://www.martineve.com/2014/06/22/typesetting-jats-bibliographies-using-csl-and-zotero/">potential for producing semantically rich JATS element-citations by using Zotero's built-in CSL engine</a>. A short while after writing that post, I wondered whether it might, instead, be possible and better to directly link <a href="https://github.com/MartinPaulEve/meTypeset">my typesetter</a> to a Zotero database. I quickly <a href="https://www.martineve.com/2014/06/23/dumping-jats-from-zotero/">mocked up a prototype</a> using an improved version of the <a href="https://github.com/smathot/qnotero">libzotero library in Qnotero</a> for the Zotero interaction.</p>
<p>A full initial implementation of this, which replaces the original meTypeset internal bibliographic database, is now <a href="https://github.com/MartinPaulEve/meTypeset/tree/zotero">available in the zotero branch of meTypeset</a>.</p>
<p>The process for Zotero typesetting in meTypeset is now, as follows:</p>
<ul>
<li>meTypeset classifies bibliography entries and places them inside mixed-citation elements</li>
<li>If the Zotero flag is passed to meTypeset ('--zotero' or '-z') then the bibliographic database kicks in</li>
<li>The Zotero handler sanitizes input through a series of regex replaces (special characters, digits etc.)</li>
<li>The Zotero handler searches the local database iteratively reducing the search string by one word from right to left until it finds a unique hit</li>
<li>If a unique hit is found, the original mixed-citation string is transcribed into a comment and a semantically rich JATS element-citation is inserted</li>
</ul>