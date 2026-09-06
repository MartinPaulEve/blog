---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2016/08/09/have-you-read-david-mitchells-cloud-atlas-if-so-which-of-the-two-very-different-versions
date: 2016-08-09
doi: https://doi.org/10.59348/azkft-pdz07
roguescholar: https://rogue-scholar.org/records/e1az9-1mh62
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mb4qbb72i
image:
  feature: Stemma.png
layout: post
ogImage: images/Stemma.png
title: Have you read David Mitchell's Cloud Atlas? If so, which of the two very different
  versions?
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mb4qbb72i"
categories:
- Publications
- Literature
kcworks: https://works.hcommons.org/records/m0r6s-jzm72
references:
- http://doi.org/10.16995/olh.82 # Eve, Cloud Atlas Version Variants OLH article
- author: Alison Flood
  date: '2016-08-10'
  title: Cloud Atlas 'astonishingly different' in US and UK editions, study finds
  type: NewsArticle
  url: https://www.theguardian.com/books/2016/aug/10/cloud-atlas-astonishingly-different-in-us-and-uk-editions-study-finds
  isPartOf:
    name: The Guardian
    type: Periodical
- author: Martin Paul Eve
  date: '2016-08-10'
  title: '“You have to keep track of your changes”: The Version Variants and Publishing History of David Mitchell''s Cloud Atlas'
  type: ScholarlyArticle
  url: http://eprints.bbk.ac.uk/id/eprint/15857
- https://commons.mla.org/deposits/item/mla:849/ # Cloud Atlas article MLA CORE repository
- title: Visualise textual variants across editions using modifications to D3.js and its Sankey plugin
  type: SoftwareSourceCode
  url: https://github.com/MartinPaulEve/SankeyTextualVariant
  isPartOf:
    name: GitHub
    type: WebSite
---

Today, my peer-reviewed journal article on the publishing history of the two substantially different versions of David Mitchell's _Cloud Atlas_ was published. You can <a href="http://doi.org/10.16995/olh.82">read the full article in all its open access glory at the <i>Open Library of Humanities</i></a>. There's also [a press release about the work](http://www.bbk.ac.uk/news/birkbeck-research-uncovers-publishing-problems-in-popular-contemporary-fiction) on Birkbeck's main site. The Guardian has also run [a great article with additional comments from David Mitchell](https://www.theguardian.com/books/2016/aug/10/cloud-atlas-astonishingly-different-in-us-and-uk-editions-study-finds).

What actually happened here, then? To cut to the chase: in 2003, David Mitchell’s editorial contact at the US branch of Random House moved from the publisher, leaving the American edition of _Cloud Atlas_ (2004) without an editor for approximately three months. Meanwhile, the UK edition of the manuscript was undergoing a series of editorial changes and rewrites that were never synchronised back into the US edition of the text. When the process was resumed at Random House under the editorial guidance of David Ebershoff, changes from New York were likewise not imported back into the UK edition. In the section entitled ‘An Orison of Sonmi~451’ these desynchronised rewritings are nearly total at the level of linguistic expression between UK and US paperbacks/electronic editions and there are a range of sub-episodes that only feature in one or other of the published editions. 

[![Stemma diagram: Mitchell's manuscript branches into the UK manuscript, leading to the P edition, and the US manuscript, leading to the E edition, French edition, and film](/images/Stemma.png)](http://doi.org/10.16995/olh.82)

The full article is also available to download from [BIROn](http://eprints.bbk.ac.uk/id/eprint/15857) (the Birkbeck, University of London institutional repository) and [MLA CORE](https://commons.mla.org/deposits/item/mla:849/).

If you wish to download the article and its supplementary files directly from this site, please also find a set of links here:

* [Article full text](/images/olh-82_eve.pdf)
* [Appendix A: Textual Variants of _Cloud Atlas_](/images/s1-olh-82_eve.pdf)
* [Appendix B: A note on the _Cloud Atlas_ variant JSON data and question/response mapping](/images/s2-olh-82_eve.pdf)
* [Appendix C: _Cloud Atlas_ variant JSON data](/images/s3-olh-82_eve.json)

The software that I wrote (derived from D3.js) that produced the Sankey visualizations in the article [is available on Github](https://github.com/MartinPaulEve/SankeyTextualVariant).