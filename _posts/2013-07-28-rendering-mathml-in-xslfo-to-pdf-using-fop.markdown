---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Rendering MathML in XSL:FO to PDF using fop
wordpress_id: 2788
wordpress_url: https://www.martineve.com/?p=2788
date: !binary |-
  MjAxMy0wNy0yOCAxNDoxMToxMyArMDIwMA==
date_gmt: !binary |-
  MjAxMy0wNy0yOCAxMzoxMToxMyArMDIwMA==
categories:
- Technology
tags:
- typesetting
comments: []
doi: "https://doi.org/10.59348/1p4y9-7f296"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2013/07/28/rendering-mathml-in-xslfo-to-pdf-using-fop"
---
<p>Another brief post on fop. I wanted to render some MathML markup inside an XSL:FO document to be converted to PDF using fop. The way to do this is to <a href="http://jeuclid.sourceforge.net/jeuclid-fop/">use JEuclid</a>. However, the JEuclid page claims to only work on fop versions 0.95beta and 0.95. Turns out this is untrue.</p>
<div style="clear:both"/>
<p>In Linux Mint/Ubuntu I got this working via the following:</p>
<ol>
<li>sudo apt-get install fop libjeuclid-fop-java</li>
<li>Edit /usr/bin/fop and add the line find_jars jeuclid-core jeuclid-fop to /usr/bin/fop</li>
</ol>





