---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2012/10/19/crude-but-helpful-typesetting-script-from-mexml
categories:
- Technology
- Open Access
- Academia
- Output
comments: []
date: 2012-10-19 19:08:08 +0200
date_gmt: 2012-10-19 18:08:08 +0200
doi: https://doi.org/10.59348/yv499-yqq65
image:
  feature: geek.png
layout: post
ogImage: geek.png
published: true
status: publish
tags:
- OA
- tools
title: Crude, but helpful, typesetting script from meXml
wordpress_id: 2440
wordpress_url: https://www.martineve.com/?p=2440
---

<p>In my quest to create a set of free and open tools for platinum, scholar-run OA journals, I've <a href="https://github.com/MartinPaulEve/MEXMLGalley/commit/351a8e28fc0adc5a1e3554b716f9bce78157620f">just committed</a> a crude, provisional script to my <a href="https://github.com/MartinPaulEve/MEXMLGalley">meXml git repository</a> that assists with typesetting into pseudo-NLM format.</p>
<p>A few notes. First of all, what does it do? The script parses markup output from the <a href="http://xing.github.com/wysihtml5/">wysihtml5 tool</a> and converts it into near-as-damnit the format I need for typesetting. The idea is that I paste a LibreOffice document (with endnotes, not footnotes) into the tool, and grab the markup it returns. This python script then parses it one step further into the format that I need to generate galleys for Orbit with the <a href="https://github.com/MartinPaulEve/MEXMLGalley/tree/master/meXml/tools">/tools/gengalleys.sh</a> tool. I still have to clean up the markup, but this has reduced the time it takes to typeset down from about 6-8 hours to about 2 hours.</p>
<p>Is this the best way to do it? Almost certainly not. Why? Because the way to do it properly would be to create a set of LibreOffice styles (or whatever mechanism it uses) and then get their tool to directly output in the format that's needed. It's also the case that I have broken compatibility with NLM standards (at present) in my implementation. This is something that I aim to gradually fix; I needed to break it at the time to Just Get It Done (trademark).</p>
<p>Is the script complete? Nope. It's pretty sloppy coding, too. Again, this is a dirty hack that I've committed in case it helps somebody.</p>
<p>Disclaimers done: enjoy!</p>