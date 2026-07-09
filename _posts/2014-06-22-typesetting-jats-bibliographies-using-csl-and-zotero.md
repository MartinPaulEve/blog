---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2014/06/22/typesetting-jats-bibliographies-using-csl-and-zotero
categories:
- Technology
- Open Access
- Academia
comments: []
date: 2014-06-22 08:08:33 +0200
date_gmt: 2014-06-22 07:08:33 +0200
doi: https://doi.org/10.59348/bz52e-q0e97
image:
  feature: geek.png
layout: post
ogImage: geek.png
published: true
status: publish
tags:
- XML
- OA
- JATS
title: Typesetting JATS bibliographies using CSL and Zotero
wordpress_id: 3139
wordpress_url: https://www.martineve.com/?p=3139
---

<p>One of the hardest parts of typesetting articles for scholarly publication in the JATS standard, especially when using homemade tools, is the bibliography. JATS (and its NLM predecessors) expects references to be broken down into their constituent components where possible in order to be semantically rich. For example:</p>
<div style="clear:both"></div>
{% highlight xml %}
      <ref id="royall">
        <element-citation publication-type="bookchapter">
          <person-group person-group-type="author">
            <name>
              <surname>Royall</surname>
              <given-names>Tyler</given-names>
            </name>
          </person-group>
          <article-title>The Contrast</article-title>
          <source>The Norton Anthology of American Literature, Vol. A: Beginnings to 1820</source>
          <person-group person-group-type="editor">
            <name>
              <surname>Franklin</surname>
              <given-names>Wayne</given-names>
            </name>
            <name>
              <surname>Gura</surname>
              <given-names>Philip F.</given-names>
            </name>
            <name>
              <surname>Krupat</surname>
              <given-names>Arnold</given-names>
            </name>
            <name>
              <surname>Baym</surname>
              <given-names>Nina</given-names>
            </name>
          </person-group>
          <publisher-name>W. W. Norton &amp; Company</publisher-name>
          <publisher-loc>New York</publisher-loc>
          <fpage>765</fpage>
          <lpage>805</lpage>
        </element-citation>
      </ref>
{% endhighlight %}
<p>This is all very well, but it also creates a problem. How do we get from the author's plaintext citation to this structured format? Parsing references is <i>hard</i>. Very hard. My closest efforts in the past have been to write a cascading regular expression engine, <a href="https://github.com/MartinPaulEve/meCite">meCite</a>, to which anybody is willing to contribute. I do intend to do more on this at some point.</p>
<p>Late last year, however, Martin Fenner was investigating whether CSL could be used to generate a JATS bibliography. His current efforts were in the <a href="https://github.com/mfenner/pandoc-jats">pandoc-JATS repository</a>. These efforts stopped, however, following <a href="http://xbiblio-devel.2463403.n2.nabble.com/CSL-Style-to-convert-to-JATS-XML-td7578866.html">a discussion on the xbiblio mailing list</a> where it was decided that CSL was not ideal for generating structured XML.</p>
<p>This may be true. However, there are a lack of viable alternatives for typesetting references. Furthermore, Zotero and Mendeley (both of which use CSL to generate their citations) have vast databases publicly available for the scholarly literature. If we could use CSL to generate valid JATS XML, this would substantially reduce the time needed to typeset a JATS bibliography. To that end, I have taken on maintenance of a fork of Martin's original efforts. Last night, with the first commits, I fixed DOI display, added book chapter support, added support for editors and changed the book title field to the correct "source" implementation. My fork can be found at the <a href="https://github.com/MartinPaulEve/JATS-CSL">JATS-CSL repo</a>.</p>
<p>While the approach may not be recommended, it is far better than nothing and I'll push it as far as I can in an effort to save some time!</p>