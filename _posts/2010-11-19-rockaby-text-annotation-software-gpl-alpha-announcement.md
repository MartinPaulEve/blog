---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/11/19/rockaby-text-annotation-software-gpl-alpha-announcement
categories:
- Programming
comments:
- author: Rockaby refactoring and abstraction | Martin Paul Eve
  author_email: ''
  author_url: http://www.martineve.com/2010/12/02/rockaby-refactoring-and-abstraction/
  content: '[...] I mentioned in my project announcement, Rockaby started life several
    years ago and it was a quick morning&#8217;s worth of hacking about [...]'
  date: 2010-12-02 09:53:51 +0100
  date_gmt: 2010-12-02 09:53:51 +0100
  id: 3567
date: 2010-11-19 16:57:29 +0100
date_gmt: 2010-11-19 16:57:29 +0100
doi: https://doi.org/10.59348/29p70-20216
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Technology
- rockaby
- GPL
title: 'Rockaby: text annotation software [GPL, alpha, announcement]'
wordpress_id: 415
wordpress_url: http://www.martineve.com/?p=415
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mlmku3c2a"
---

<p><img class="alignright" src="http://www.martineve.com/images/logo.png" alt="Rockaby" /><br />
till in the end<br />
the day came<br />
in the end came<br />
close of a long day<br />
when she said<br />
to herself<br />
whom else<br />
time she stopped<br />
-- Samuel Beckett, Rockaby</p>
<p>Today marks the first release of the source for my book annotation software, Rockaby. At present, the base installation is up and running at <a href="http://gr.pynchon.net/">http://gr.pynchon.net/</a> which forms the Online Gravity's Rainbow Reference.</p>
<p><strong>So, what is Rockaby.</strong><br />
Rockaby is a tool to annotate long, complex, or otherwise require-explanation texts. It features a footnote referencing system, automatic character and reference index linkup and a plethora of other features.</p>
<p>Here's the homepage:<br />
<a rel="attachment wp-att-416" href="http://www.martineve.com/2010/11/19/rockaby-text-annotation-software-gpl-alpha-announcement/screen1/"><img title="Gravity's Rainbow Reference running Rockaby" src="http://www.martineve.com/wp-content/uploads/2010/11/screen1.png" alt="Gravity's Rainbow Reference running Rockaby" width="400" height="405" /> </a></p>
<p>...and an example of the automated reference generation:<br />
<a rel="attachment wp-att-417" href="http://www.martineve.com/2010/11/19/rockaby-text-annotation-software-gpl-alpha-announcement/screen2/"><img title="Rockaby referencing" src="http://www.martineve.com/wp-content/uploads/2010/11/screen2.png" alt="Rockaby referencing" width="400" height="222" /></a></p>
<p><strong>What stage is it at?</strong><br />
Rockaby was originally written in .NET, but I have just spent the last day or so converting it to Django and this is the released form. As such, the code is new and has several setbacks:</p>
<ul>
<li>Too much heavy lifting is being done in the views from the originally hackish .NET application</li>
<li>Many aspects are currently hardcoded to my Pynchon annotation project</li>
<li>Generally needs to be made more pythonic</li>
<li>Admin interface virtually non-existent</li>
</ul>
<p>I, therefore, would be very interested to hear from any Django developers who would like to participate.</p>
<p><strong>How is it licensed?</strong><br />
The project is licensed under GPL v3.<br />
<a rel="attachment wp-att-418" href="http://www.martineve.com/2010/11/19/rockaby-text-annotation-software-gpl-alpha-announcement/gplv3-127x51/"><img title="GPL v3" src="http://www.martineve.com/wp-content/uploads/2010/11/gplv3-127x51.png" alt="GPL v3 logo" width="127" height="51" /></a></p>
<p><strong>How can I get the source?</strong><br />
The source code is hosted at the <a href="http://code.google.com/p/rockaby/">Google Code repository</a>. If you have some improvements/patches, email me (or comment below) and, pending review, I can add you to the team.</p>
<p><strong>Why the name?</strong><br />
In addition to referencing one of my favourite plays, it also functions, from the quotation above, as an auto-critical statement on exegesis.</p>