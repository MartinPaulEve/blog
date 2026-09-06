---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2013/07/28/determining-glyph-availability-for-fop
categories:
- Publishing Technology
comments: []
date: 2013-07-28 12:40:34 +0200
date_gmt: 2013-07-28 11:40:34 +0200
doi: https://doi.org/10.59348/6agph-pja34
roguescholar: https://rogue-scholar.org/records/4yggf-6kw42
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mgggzox2f
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- FOP
- typesetting
title: Determining glyph availability for FOP
wordpress_id: 2782
wordpress_url: https://www.martineve.com/?p=2782
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mgggzox2f"
kcworks: https://works.hcommons.org/records/05h9x-ec017
references:
- title: 'FileFormat.Info: The Digital Rosetta Stone'
  type: WebSite
  url: http://www.fileformat.info
- title: CHECK MARK (U+2713) Font Support
  type: WebPage
  url: http://www.fileformat.info/info/unicode/char/2713/fontsupport.htm
  isPartOf:
    name: FileFormat.Info
    type: WebSite
---

<p>I've just spent the past hour grappling with getting FOP to render the Unicode glyph for a checkmark (U+2713) in PDF output from XSL:FO. I thought I'd share a few things I learnt along the way (that make me feel a bit silly for not knowing them already).</p>
<div style="clear:both"/>
<p>The type of errors I was getting were:</p>

{% highlight bash %}
Glyph "✓" (0x2713, checkmark) not available in font "Times-Roman".
{% endhighlight %}

<p>Some observations after messing around for far too long:</p>
<ol>
<li>Fop does not support fallback to a secondary font on a character-by-character basis. If you need a glyph to be rendered that isn't present in your font, well, bad luck. (Unless you specifically tweak your XSL:FO document, which isn't viable in my case.)</li>
<li>There is no way, as far as I can see, that you can map a specific character to use a different font.</li>
<li>There is a <a href="http://www.fileformat.info">great resource at fileformat.info</a> that will <a href="http://www.fileformat.info/info/unicode/char/2713/fontsupport.htm">tell you what fonts support your glyphs</a>.</li>
<li>Just use DejaVu Sans and save yourself a lot of tweaking.</li>
</ol>