---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2020/04/10/zotero-and-open-access-books
date: 2020-04-10
doi: https://doi.org/10.59348/ajrhh-f4r08
roguescholar: https://rogue-scholar.org/records/damjz-kmg35
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m67yern2s
image:
  feature: oa.png
layout: post
ogImage: images/oa.png
title: Zotero and auto-downloading open access books
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m67yern2s"
categories:
- Scholarly Communications
- Programming
---

This bank holiday, I wanted to spend some time playing around with Zotero's automatic ingest of open access books. There are some problems with this.

For recap, Zotero offers users a way easily to ingest items using built-in metadata on a page. It supports Dublin Core, various RDF implementations, and COinS.

Here's the problem, though: if you want automatic lookup by ISBN, you have to use the COinS translator/provide COinS metadata. This has a fallback system where, if there isn't much metadata given, it looks it up.

However, if you want an automatic file download of the associated PDF, which will become increasingly common in a digital and OA world, you _cannot_ use COinS, as it doesn't have this provision. This gives a nasty catch-22: all I really wanted was to be able to embed an ISBN and a citation_pdf_url and have Zotero do the lookup and save the file. However, out of the box there is no easy way to do this.

I took this as an opportunity for a learning experience in writing Zotero translators. I [wrote a translator for Zotero](/images/CustomBook.js) that will allow you to embed the following metatags in a document and then to have Zotero fish it out:

<pre>
	&lt;meta name="book_pdf_url" content="http://eprints.bbk.ac.uk/id/document/158876" /&gt;
	&lt;meta name="book_isbn" content="9781503609365" /&gt;
</pre>

A morning well wasted, I mean, spent!