---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2014/06/03/a-research-tool-i-want-but-probably-wont-get-cross-referenceintersect-bibliographies-of-books-and-articles
categories:
- Scholarly Communications
- Open Access
comments: []
date: 2014-06-03 09:00:48 +0200
date_gmt: 2014-06-03 08:00:48 +0200
doi: https://doi.org/10.59348/w86n1-sk761
roguescholar: https://rogue-scholar.org/records/973yw-gw165
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mf3cwnx2t
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- OA
- tools
title: 'A research tool I want (but probably won''t get): cross-reference/intersect
  bibliographies of books and articles'
wordpress_id: 3129
wordpress_url: https://www.martineve.com/?p=3129
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mf3cwnx2t"
kcworks: https://works.hcommons.org/records/yrzyp-3w543
---

<p>I was thinking last week about the process of starting any new project -- and it's fairly clear cut. When I am conducting an initial literature review, I head off to the British Library and order ten or so books/articles on the subject that I want to investigate (provided there are 10 articles/books). I then go through the bibliographies and check which entries appear in all ten. I then have a list of core readings that should bring me up to speed.</p>
<p>This process is time consuming and boring. At this point in the process, the names often mean little to me. It is, after all, hard to get excited about abstract titles of books by people whose work you've yet to encounter. There is, however, definitely a better way to do this that I can think of off the top of my head. It's probably also true that some commercial provider already does this; I have not found one that does it adequately for my discipline, however, and that includes books.</p>
<p>What we need is the ability to give a list of books/articles to a piece of software that then just tells me the citations-in-common among all of them.</p>
<p>This should not be hard to implement. In theory. In the Journal Article Tag Suite (JATS) and its book analogue, references are encoded (if done properly) like this:</p>
{% highlight xml %}
      <ref id="ID94a8f57d-19a5-40bf-8f5c-f601517c2bcf">
        <element-citation publication-type="book">
          <person-group person-group-type="author">
            <name>
              <surname>Eve</surname>
              <given-names>Martin Paul</given-names>
            </name>
          </person-group>
          <source>Pynchon and Philosophy</source>
          <date>
            <year>2014</year>
          </date>
          <publisher-loc>New York</publisher-loc>
          <publisher-name>Palgrave Macmillan</publisher-name>
        </element-citation>
      </ref>
{% endhighlight %}
<p>Likewise, an article (with a DOI) is tagged thus:</p>
{% highlight xml %}
      <ref id="Tina">  
        <element-citation publication-type="journal" publication-format="web">
          <person-group person-group-type="author">
            <name>
              <surname>K&#228;kel&#228; Puumala</surname>
              <given-names>Tiina</given-names>
            </name>
          </person-group>
          <article-title>&#8216;There Is Money Everywhere&#8217;: Representation, Authority, and the Money Form in Thomas Pynchon's <italic>Against the Day</italic></article-title>
          <source>Critique: Studies in Contemporary Fiction</source>
          <date>
            <year>2013</year>
          </date>
          <issue>2</issue>
          <volume>54</volume>
          <pub-id pub-id-type="doi">10.1080/00111619.2011.553846</pub-id>
        </element-citation>
      </ref>
{% endhighlight %}
<p>Given, then, that we have semantically rich encodings of this information in many cases, it would seem trivial to take a set of articles and books encoded in this format and to cross-reference them against one another. Except... we don't have access in most cases to the XML. It has been decided that what researchers solely need (especially in the humanities) is text and argument without due thought to the research process that envelops our reading methodologies. Reading is, after all, not a uniform process; the way in which we read differs radically over the course of a project and depending upon the type of project. My utilitarian literature review method will give way to deep reading at a different stage.</p>
<p>So, the first problem is access: publishers do not give us the XML and they do not give us the tools to perform this kind of operation. They also frequently do not work together, so it is unlikely that, even if one publisher came up with such a system, it would be possible to use any scholarly material with such a system. This makes it very hard for someone such as me -- who likes to spend his weekends doing computer programming tasks to make cool little experiments -- to just "have a go" or to stumble upon a way of making it work, as I did with <a href="https://github.com/MartinPaulEve/meTypeset">meTypeset</a>.</p>
<p>The second problem is the lack of DOI coverage. While it is possible to filter the non-DOI entries and parse them using text methods, there is a far greater chance of error than if we had a DOI assigned to every item. After all, to either XPATH or regex match a DOI is utterly trivial. But books do not frequently have DOIs assigned. And they usually don't cite items that do have a DOI by using it. So, besides from the fact that there is a vast digital preservation structure being under-used, it also impedes development of tools such as this that I'm proposing that could really help with my day-to-day research practice.</p>
<p>These are the kind of things that people don't usually imagine (at least in my world) when they think about open access. However, if we can begin to envisage scenarios such as this -- which are not techno-fetishistic or determinist, but rather take a social problem and then apply technology to help solve it -- there's a chance that more will become interested.</p>