---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2014/02/26/mathml-support-in-the-metypeset-typesetter
categories:
- Publishing Technology
- Programming
comments: []
date: 2014-02-26 20:17:17 +0100
date_gmt: 2014-02-26 20:17:17 +0100
doi: https://doi.org/10.59348/ftw1m-hbx08
roguescholar: https://rogue-scholar.org/records/89c4t-6cz16
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mfgpjfm2h
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- OA
title: MathML support in the meTypeset typesetter
wordpress_id: 3043
wordpress_url: https://www.martineve.com/?p=3043
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mfgpjfm2h"
---

<h1>Diversity of material</h1>
<p>One of the big challenges that we face in designing an open source scholarly typesetter is ensuring that a diverse range of papers can accurately be parsed by the system. I come from a humanities background and know what articles from those disciplines look like. I do not necessarily know the structure and format of an article from the biomedical sciences.</p>
<p>However, one of the core differences between the disciplines that I have been handling today is our implementation of MathML. MathML is a markup language (ML) that handles mathematical equations. It provides a way to represent, within a linear format, the complex graphical symbols used in formulae by scientists, mathematicians and some philosophers of logic. The JATS (Journal Article Tag Suite) standard includes support for MathML meaning that it is possible to encode mml:math blocks inside paragraphs in an NLM/JATS document that can be rendered by any compatible galley production unit.</p>
<h1>The two cultures</h1>
<p>There is a problem however. Our assumed most common input format is Microsoft Word's docx format, which is a compressed collection of XML documents. However, rather than opting for MathML, Microsoft decided to invent their own standard: OMML (see <a href="http://idippedut.dk/post/2008/01/30/Do-your-math-OOXML-and-OMML.aspx">‘Do Your Math - OOXML and OMML (Updated 2008-02-12)’ 2008</a>). This allows them greater flexibility for their formatting implementation, but critics would note that such plurality goes against the concept of a “standard” and fragments the field. It also creates a painful problem for our typesetter.</p>
<p>Our input documents, therefore, are in OMML. Our output format needs to be standard MML. What is to be done?</p>
<p>The answer, it turns out, was surprisingly simple. The OxGarage stack, which sits beneath meTypeset as its core engine (in a modified format), has a beta transform procedure for OMML to MML. We also, though, have a fully fledged implementation from Microsoft. However, this is not something we can distribute and would only be of personal use if one had a Microsoft Office license.</p>
<p>So, what we have done is this: by default used the OxGarage beta transform stack. If the user passes the “-p” flag (“--proprietary”) then we invoke our wrapper that will use the fuller Microsoft transform.</p>
<p>A couple of lines added to the XML transform for the TEI to JATS phase and we're there. I also added a few lines to make sure that other parts of the transform stack don't try to alter MathML code.</p>
<h1>Cite this article</h1>
<p>Please include the DOI in your citation: <a href="http://dx.doi.org/10.6084/m9.figshare.944613">http://dx.doi.org/10.6084/m9.figshare.944613</a><br />
You can <a href="https://www.martineve.com/lens-martineve/index.html?url=https://www.martineve.com/lens-martineve/data/2014-02-26.xml">view this post's XML with lens</a>.</p>