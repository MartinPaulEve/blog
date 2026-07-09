---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2016/06/09/identifying-26gb-of-json-novel-data
date: 2016-06-09
doi: https://doi.org/10.59348/m0te2-e1152
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: Identifying 26GB of JSON Novel Data
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mberrip2i"
---

For part of one of my current research projects I have a pretty large (26GB) corpus of digitized JSON novels. I'm interested in ingesting these and then performing various methods of authorship attribution to them using delta, nearest shrunken centroid and other techniques.

The two initial challenges here for the data cleanup are:

1. The OCR isn't perfect (in fact, it's very dodgy in some cases)
2. I have a set of metadata, but no correlation to the actual filenames

I've been trying to think about the best way that I can handle these two cleanup problems in one go and I think I have an answer. The first answer is that I've asked the original supplier whether or not they actually have metadata records that have the filenames. This would solve problem number two, but not the first one (which could have severe consequences for any stylometric analyses).

The other option that I thought of would be to parse the "title" field from the JSON and try to look it up in the metadata record-set that I have.

So, for instance, a well-scanned edition might have the following record:

    [5, "COO-EE TALES OF AUSTRALIAN LIFE"]

While an edition with terrible OCR would have:

    [3, "<\u00a9jcbfrrp'. ..fcitioiu *4 JVMW W.ALY TO PAY OLD DEBTS ... etc

So, a possible solution to both problems seems to come out here. If I insist that the title (stripped of punctuation) must be accurate and well scanned, AND I can find a metadata record for it, I'll probably end up with a reduced set of texts but might also possibly distinguish between good and bad data. Since I'm interested in knowing whether certain novels aesthetically correspond more or less closely to my target text (in terms of author signals) compared to a set of canonical novels, this might be an acceptable trade-off.

Continuing to think about it.