---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/05/16/xss-in-excess-a-learn-xss-tool
categories:
- Information Security
comments: []
date: 2007-05-16 13:04:45 +0200
date_gmt: 2007-05-16 13:04:45 +0200
doi: https://doi.org/10.59348/xwgby-3hj54
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- information security
- XSS
title: 'XSS in eXceSS: A "learn-XSS tool"'
wordpress_id: 285
wordpress_url: http://pro.grammatic.org/post-xss-in-excess-a-learnxss-tool-14.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mnrk2we2s"
---

<p>kishord today presents a tool, called <a href="http://wasjournal.blogspot.com/2007/05/xss-in-excess.html" title="XSS in eXceSS">XSS in eXceSS</a> and hosted by <a href="http://mario.heideri.ch/" title=".mario's blog">.mario</a> that will allow you test attack vectors against a page in different contexts. On top of that it also incorporates <a href="http://groups.google.de/group/php-ids" title="PHP IDS">PHP IDS</a>, allowing you to skip whichever rules you choose.</p>
<p>From kishord's post:</p>
<blockquote><p> It takes the input via various get parameters and leads to different areas in the HTML page. E.g. parameter freehtml=ATTACK_VECTOR will place the injection in to the HTML body. There are more than 25 such parameters which lead to different XSS areas.</p>
<p>Please read the usage notes on the <a href="http://h4k.in/xssinexcess">page</a>.<br />
In order to make it a learning tool, it is coupled with PHP IDS with some modifications. It lets the user choose which IDS rules to skip. Thus each XSS area now can be XSSed by challenging different filters. E.g. If you are able to attack in an area where only the &lt;script&gt; can cause an injection, (E.g. html body, ummm, well ignore other cases for now) then you have to ask the page to skip the filter that detects script tag.</p></blockquote>
<p>Good stuff!</p>