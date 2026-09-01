---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2013/03/29/exposing-xml-data-for-orbit
categories:
- Publishing Technology
comments: []
date: 2013-03-29 19:59:51 +0100
date_gmt: 2013-03-29 19:59:51 +0100
doi: https://doi.org/10.59348/e431n-pfb44
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- XML
- XSLT
title: Exposing XML data for Orbit
wordpress_id: 2654
wordpress_url: https://www.martineve.com/?p=2654
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mgu7ei32h"
---

<p>Although, for now, this will be of limited interest/use to probably most readers of the journal, I today undertook the necessary work (by which I mean: cleaning up for compliance!) to expose the XML files that power the typesetting behind my journal of Pynchon studies, <a href="https://www.pynchon.net">Orbit: Writing Around Pynchon</a>.</p>
<p>As you can see if you visit <a href="https://www.pynchon.net/owap/issue/view/1">Issue 1</a>, all the articles now have their XML available for download. I intend to sequentially work through the rest of our published articles to expose this data. Let me explain what this means and then why I think it's important.</p>
<p>The way that I construct articles for the journal is, after successful peer review, to transcribe the word documents that we are sent into extensible markup language (XML) under a document type definition provided by the National Library of Medicine. This <a href="http://dtd.nlm.nih.gov/publishing/tag-library/3.0/index.html">Journal Publishing Tagset</a> specifies how this document should be formed for compliance and they provide some sample tools to produce output.</p>
<p>Once I've got the XML file together -- and this can be no small job in the case of complex citations -- I run it through my custom galley production suite, <a href="https://github.com/MartinPaulEve/MEXMLGalley">meXml</a>. Running the <a href="https://github.com/MartinPaulEve/MEXMLGalley/blob/master/meXml/tools/gengalleys.sh">tools/gengalleys.sh</a> script produces PDF and XHTML output from the same file, so I know that they are synchronised. I can then, also (<a href="http://help.crossref.org/#nlm-to-crossref-conversion">with any luck in the near future</a>), do a transform on the XML to produce the documents that I need to send to CrossRef.</p>
<p>Why do this, though? Why not just botch together a PDF and HTML exported from Word? A few important reasons:</p>
<ul>
<li>The XHTML that is produced should be 100% W3C standards compliant, which increases accessibility for those with, for instance, visual impairments.</li>
<li>The documents will always be synchronised, even if another version is required.</li>
<li>Data mining. If people want to work out what scholars are doing in our field, they now have the raw data at their disposal, under a CC-BY license.</li>
<li>Digital preservation. If I get hit by a bus tomorrow and, over the coming years, the PDF becomes obsolete while XHTML isn't the way that primarily consume texts, having the XML available will allow others to forward-migrate the content, should they so wish. This is just another of the strategies that we are employing, alongside CLOCKSS and LOCKSS preservation, to ensure the persistence of the journal beyond our lifespans.</li>
</ul>