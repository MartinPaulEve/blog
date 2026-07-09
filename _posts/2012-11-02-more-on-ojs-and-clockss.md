---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2012/11/02/more-on-ojs-and-clockss
categories:
- Technology
- Open Access
- Academia
comments: []
date: 2012-11-02 11:46:59 +0100
date_gmt: 2012-11-02 11:46:59 +0100
doi: https://doi.org/10.59348/vzmhd-b1w63
image:
  feature: oa.png
layout: post
ogImage: images/oa.png
published: true
status: publish
tags:
- OJS
title: More on OJS and CLOCKSS
wordpress_id: 2471
wordpress_url: https://www.martineve.com/?p=2471
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mhngkk52q"
---

<p>Frequent readers <a href="https://www.martineve.com/2012/10/24/open-journal-systems-now-supports-archiving-with-clockss-out-of-the-box/">may recall</a> that I had implemented CLOCKSS support in OJS. I'm sad to say that the original commit was flawed and it was decided that <a href="http://pkp.sfu.ca/bugzilla/show_bug.cgi?id=7958#c5">the best thing to do was to revert it</a>, the reason being that there was no selective option to turn off the CLOCKSS manifest.</p>
<p>Anyway, after extensive work, <a href="https://github.com/pkp/ojs/pull/49">I've re-done the patch</a> so that OJS has fully customizable CLOCKSS support that can be enabled and disabled independently from LOCKSS. Fingers crossed this one gets merged!</p>