---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2014/04/17/bitmask-values-for-wtbllook-wval-attribute-in-ooxml
categories:
- Technology
comments: []
date: 2014-04-17 13:01:18 +0200
date_gmt: 2014-04-17 12:01:18 +0200
doi: https://doi.org/10.59348/ymejq-efd49
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Technology
title: Bitmask values for w:tblLook w:val attribute in OOXML
wordpress_id: 3096
wordpress_url: https://www.martineve.com/?p=3096
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mf76b4r2n"
---

<p>For my own reference:</p>
<div style="clear:both"/>
<table>
<tr>
<td>0x0020</td>
<td>Apply first row conditional formatting</td>
</tr>
<tr>
<td>0x0040</td>
<td>Apply last row conditional formatting</td>
</tr>
<tr>
<td>0x0080</td>
<td>Apply first column conditional formatting</td>
</tr>
<tr>
<td>0x0100</td>
<td>Apply last column conditional formatting</td>
</tr>
<tr>
<td>0x0200</td>
<td>Do not apply row banding conditional formatting</td>
</tr>
<tr>
<td>0x0400</td>
<td>Do not apply column banding conditional formatting</td>
</tr>
</table>
<p>If no bitmask on the row, it is inherited from table-level properties.</p>
<p>Seems to be set to 04A0 when heading is on, as opposed to 0480 when off.</p>
<p>Given that 0x0400 and 0x0080 seem to be irrelevant, it looks as though headings are controlled by: 0×0020  Apply first row conditional formatting</p>