---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2013/12/27/why-im-a-fan-of-open-source-software-an-argument-by-anecdoteexample
categories:
- Technology
- Linux
comments: []
date: 2013-12-27 18:05:10 +0100
last_modified_at: 2026-09-06
date_gmt: 2013-12-27 18:05:10 +0100
doi: https://doi.org/10.59348/ad674-42658
roguescholar: https://rogue-scholar.org/records/f6mg9-es402
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mftd6nh2t
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Linux
- Python
title: 'Why I''m a fan of open source software: An argument by anecdote/example'
wordpress_id: 2967
wordpress_url: https://www.martineve.com/?p=2967
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mftd6nh2t"
kcworks: https://works.hcommons.org/records/mta7t-yns40
references:
- title: 'GitHub - m0sia/pyParrotZik: Python Parrot Zik API and tools'
  type: SoftwareSourceCode
  url: https://github.com/m0sia/pyParrotZik
  isPartOf:
    name: GitHub
    type: WebSite
- title: 'Add second option for icon paths on Linux by MartinPaulEve · Pull Request #1 · m0sia/pyParrotZik'
  type: WebPage
  url: https://github.com/m0sia/pyParrotZik/pull/1
  isPartOf:
    name: GitHub
    type: WebSite
---

<p>An argument by anecdote.</p>
<p>My prized Christmas present this year (which I obtained by selling a load of old electronics that I didn't want/need) was a pair of Parrot Zik headphones. They're wonderful. They paired with my Android phone flawlessly and they also connected with superb ease to my Linux installation which is my primary setup.</p>
<p>However, I have now spent several hours trying to get them to work under Windows 7. Will they pair? Of course they won't. Apparently you need to install a different Bluetooth stack. After much registry hacking and following circular trails of advice from Microsoft, I have up and plugged them in manually.</p>
<p>Switching back into my Linux installation I found that somebody had written <a href="https://github.com/m0sia/pyParrotZik">a great-looking cross-platform indicator icon for the headphones</a>, having reverse engineered the protocol. I cloned the git repo, installed the dependencies (todo: write list of python modules required) and, bang, it fired up and worked.</p>
<p>Now, it didn't work flawlessly. The icon in the indicator was showing up as "not found". Hmmm, I thought. Is this going to be another Windows fiasco? No, it is not. I delved into the code, because I can(!) so I can actually see what's wrong. About five minutes later I'd written a fix for the problem and <a href="https://github.com/m0sia/pyParrotZik/pull/1">committed it back as a pull request</a> to the original author so that everyone can benefit.</p>
<p>Now, the problems are of a different magnitude: writing and debugging a full low-level bluetooth stack is likely beyond my ability and willpower. However, I will never know. All I have in that case are compiled binaries that I cannot fix. By contrast, in the open context, I've given something, admittedly small, but useful, back.</p>