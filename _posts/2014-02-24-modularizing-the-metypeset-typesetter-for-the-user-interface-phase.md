---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2014/02/24/modularizing-the-metypeset-typesetter-for-the-user-interface-phase
categories:
- Technology
- meTypeset
comments: []
date: 2014-02-24 19:30:50 +0100
date_gmt: 2014-02-24 19:30:50 +0100
doi: https://doi.org/10.59348/wped7-g2j17
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- OA
- typesetting
title: Modularizing the meTypeset typesetter for the user interface phase
wordpress_id: 3033
wordpress_url: https://www.martineve.com/?p=3033
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mfobrk52r"
---

<h1>Modularizing the Project</h1>
<p>Today brings with it some notable changes to my scholarly article XML (NLM/JATS) typesetter (<a href="https://github.com/MartinPaulEve/meTypeset/tree/dev">meTypeset</a>). First off, the project is now nicely <a href="https://github.com/MartinPaulEve/meTypeset/commit/5662b3aeda62b9ee7a8bf009ce7b5cc77ed95fa6">handling user supplied captions</a> to figures, so long as they are in the format &#8220;Figure 1: a figure caption&#8221;.</p>
<p>The second, more important change, that I've implemented, however, is to begin to modularize the project and to add individual command line hooks for different functions. So it's now possible to run specific functions. This will allow us to begin to build a user interface on top of the software.</p>
<p>The envisaged process at the moment is:</p>
<ol>
<li>
<p>web service calls meTypeset on document</p>
</li>
<li>
<p>user is presented with WYSIWYG editor/step-by-step walkthrough to fix aspects</p>
</li>
</ol>
<p>The way in which the step</p>
<h1>The reference linker</h1>
<p>A good example of this is the new options available via the reference linker. The reference linker is the portion of meTypeset that scans through documents looking for parenthetical references (Eve 2014 etc.) and then tries to link such items to valid ref-list/ref entries.</p>
<p>We have a moderately good success rate on such aspects. If it's done properly, with semicolons between bracketed entries and there is a single ref-list/ref entry that matches all the space separated and special-character normalized components of the reference, then we can link it no problem.</p>
<p>If, however, there are entries we can't parse, we need a user interface to handle this. While this will be web-based eventually, I today added an &#8211;interactive flag to the typesetter that will allow a command line input aspect, like this:</p>
<p><a href="https://www.martineve.com/wp-content/uploads/2014/02/image1.png"><img src="https://www.martineve.com/wp-content/uploads/2014/02/image1.png" alt="meTypeset interactive" width="813" height="933" class="alignnone size-full wp-image-3034" /></a></p>
<p>Figure 1: meTypeset running in interactive mode</p>
<p>This interface, which is based on the excellent <a href="https://github.com/sampsyo/beets/">beets music tagger</a>, will be of great personal use to me when I typeset articles for <a href="https://www.pynchon.net/">Orbit</a> (and for my hoped-for move to <a href="https://github.com/elifesciences/lens">lens viewer</a> at some point). Basically, here the user can select a specific option (Skip, Delete (remove the stub xref element), Enter search (>search the reference list for the correct entry), enter Link id (give an absolute element ID attribute to function as the rid attribute), or Abort the entire process).</p>
<p>This is just a start, but if we can develop a slick UI for the web on top of this, we will be solving a substantial problem in the currently commercial toolchain.</p>
<h1>Cite this article</h1>
<p>Please include the DOI in your citation: <a href="http://dx.doi.org/10.6084/m9.figshare.942425">http://dx.doi.org/10.6084/m9.figshare.942425</a><br />
You can <a href="https://www.martineve.com/lens-martineve/index.html?url=https://www.martineve.com/lens-martineve/data/2014-02-24.xml">view this post's XML with lens</a>.</p>