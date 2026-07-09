---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2013/03/26/crossref-dois-and-preparing-for-future-assignment
categories:
- Technology
- Open Access
comments: []
date: 2013-03-26 12:14:05 +0100
date_gmt: 2013-03-26 12:14:05 +0100
doi: https://doi.org/10.59348/7tn6f-ewz33
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Technology
title: CrossRef, DOIs and Preparing for Future Assignment
wordpress_id: 2642
wordpress_url: https://www.martineve.com/?p=2642
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mguxor22u"
---

<p>It is a fundamental part of the PILA agreement that is signed when a publisher joins CrossRef that they will link to other articles using their DOIs. So, for example, if I cite an article in a journal that has a DOI, I must ensure that I use that DOI. If it doesn't have a DOI, then I needn't link to the article using the DOI.</p>
<p>A question suddenly occurred to me the other day, though: what happens if, after I've published an article, an article that I cited that did not previously have a DOI is assigned one by its publisher? Do I have a requirement to update? Apparently: yes.</p>
<p>To-date, because I am a low-volume publisher, I have been using the <a href="http://www.crossref.org/SimpleTextQuery/">Simple Text Query interface</a> to parse citations and work out where there are DOIs. The problem is, there is no way here for me to be notified of future changes or updates.</p>
<p>The answer, which Ed Pentz gave me on Twitter, was either to re-send queries periodically, or to use <a href="http://help.crossref.org/#stored-queries">stored queries</a>. Realizing that I needed, then, to move towards some kind of automation, I've put together a simple Python script to assist in this process. It's called <a href="https://github.com/MartinPaulEve/crossRefQuery/">crossRefQuery</a> and it does what it says, enabling future matches to be emailed to you.</p>
<p>You create a text file containing:</p>
<p>Username<br />
Password<br />
Email<br />
UniqueQueryID<br />
Citation1...<br />
Citation2...</p>
<p>and pipe this into the script. It then returns the XML output to stdout.</p>
<p>Given that <a href="https://www.pynchon.net">Orbit</a> runs off NLM-XML for typesetting, I will probably also write something that will convert NLM citations to CrossRef query format and put that online too. However, <a href="http://www.alluvium-journal.org">Alluvium</a> just runs off plain-text typesetting, so having the formatted citation search option is handy.</p>
<p>Hope it helps someone. Oh, but you will need to contact CrossRef support to get the API enabled on your account.</p>