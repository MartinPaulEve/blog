---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2015/06/07/visualizing-gravitys-rainbow
categories:
- Digital Humanities
- Thomas Pynchon
date: 2015-06-07
doi: https://doi.org/10.59348/y831w-1h790
image:
  feature: post_images/GR2.jpg
layout: post
ogImage: images/post_images/GR2.jpg
published: true
tags:
- textplot
- Pynchon
title: Visualizing Gravity's Rainbow
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mcpnpz72s"
---

At this year's _Canadian Congress of Humanities and Social Sciences_ I had the pleasure of attending a talk by David McClure in the digital humanities strand on his visualization tool, _TextPlot_.

I won't go into the technical details of what TextPlot does, because David has done so adeptly in a [series of posts on his blog](http://dclure.org/tag/textplot/). Essentially, though, the tool allows for the creation of a force-directed graph of the top n terms in a text after computing a probability density function (using kernel density estimation) filtered by Bray-Curtis dissimilarity. This results in a map of clustered and connected terms within a specific distance; which terms occur "together" within a specified distance and are, therefore, most closely connected.

Immediately after the session I decided to play around with this for Thomas Pynchon's epic, 1973 novel, _Gravity's Rainbow_. The resultant Gephi visualization of the top 1,000 terms (there are some problems with accents cutting some words short, like "Peenemünde") looks like this:

[![Gephi Map of Gravity's Rainbow](/images/post_images/GR2.jpg)](/imagezoom/#image-files/gr)

You can also click the image to explore the network using the [zoomable image viewer](http://dclure.org/logs/a-citable-deep-zooming-image-viewer/) that David also built.

# Critical observations
There are several features of this network map that are worthy of comment:

* Character names are all peripheral while abstract terms, things and actions are usually more strongly linked. This seems to tie in with most assessments of Pynchon's character models. However, this is a common linguistic model for novels that is to be expected, except in the case of central characters in narratives; absent in _GR_.

* Characters are correctly grouped. [Pökler \[badly split as kler\], Weissman and Ilse](/imagezoom/#image-files/gr/0.7918/0.5668/1.1458), for instance. [Roger, Jessica and Pointsman](/imagezoom/#image-files/gr/0.8280/0.8325/1.1458). [Tchitcherine, Enzian and the Schwarzcommando/Herero](/imagezoom/#image-files/gr/0.1778/0.5007/1.1458). [Bodine, Squalizdozzi and Rocketman](/imagezoom/#image-files/gr/0.2791/0.1484/1.1458). [Bianca, Greta, Margherita and the Anubis](/imagezoom/#image-files/gr/0.8648/0.1366/1.1458).

* Compared to running the same process on, say, _War and Peace_, as has David, the groupings are incredibly dense, for the most part. This probably structurally contributes to the paranoid associations of connectedness that is the novel's desired aesthetic.

* (My) critical assertions that a (nostalgic?) looking "back" as key to Pynchon's works (in my study focused on _Lot 49_) seem here to have some validity but one that is less centrally remarked upon in _GR_; the term "back" is one of the central and [most connected nodes in the novel](/imagezoom/#image-files/gr/0.5050/0.3920/1.1458).

* There's an interesting metahistorical clump around the 7pm mark; [history, power, political, system, structure and possibilities are all clustered](/imagezoom/#image-files/gr/0.3986/0.7062/1.1458). This might indicate that the metahistorical elements of/observations made by the text are not well integrated with the narrative as a whole.

* Some temporal terms cluster at about 5:30pm along with some value judgements. [Autumn, age, ancient, years, winter, memory](/imagezoom/#image-files/gr/0.6354/0.6553/1.1458). Twinned with terrible, brown.

* The most isolated narrative is [Byron the Bulb](/imagezoom/#image-files/gr/0.0401/0.4003/1.1458), seen at 9pm on the far left. This makes sense as the text breaks off to relate this parable in complete disconnection from anything else in the novel.

* Thomas Gwenhidwy, a peripheral character but one who occurs in multiple contexts is [likewise isolated](/imagezoom/#image-files/gr/0.6169/0.8712/1.1458), but better connected.

* Rocket is nowhere near so central as one would suppose.

Perhaps most interestingly, it strikes me that, on a first pass, the clustering in this network focuses on areas to which there has been substantial critical attention within the text. Roger and Jessica; the Anubis; Rocketman; Weissman, Pökler and Ilse; Katje and the octopus, Grigori; Enzian and Tchitcherine; Byron the Bulb. In this way, the algorithm correct identifies many of the scenes, amid this convoluted novel, that critics have deemed important. There are, however, areas that have had critical attention that are not here well modelled: perhaps, most notably, the launch of the 0000; Slothrop's disintegration.

# Semantic fields within the novel
I want to do much more playing with this to ascertain whether different parameters (and even different algorithmic approaches to plotting density/clustering) yield wildly different results.

However, it's worth also closing with a few thoughts about why some episodes in this novel are clearly distinct in this visualization technique while others are integrated and dispersed. The method that TextPlot uses to generate its data is based on linguistic linkage. As [David puts it](http://dclure.org/essays/mental-maps-of-texts/):

> I was thinking about the way that words distribute inside of long texts – the way they slosh around, ebb and flow, clump together in some parts but not others. Some words don’t really do this at all – they’re spaced evenly throughout the document, and their distribution doesn’t say much about the overall structure of the text. This is certainly true for stopwords like “the” or “an,” but it’s also true for words that carry more semantic information but aren’t really associated with any particular content matter. [...] Other words, though, have a really strong semantic focus – they occur unevenly, and they tend to hang together with other words that orbit around a shared topic.

_Gravity's Rainbow_ has been assessed by many readers as a text that works to generate a feeling, among its readers, that everything may be connected (as a form of conspiratorial plot) and that, therefore, it might equally be the case that nothing is connected. Pynchon terms these paranoia (total connectedness) and anti-paranoia (utter disconnect).

An initial plot of the text in this way allows us to start to consider whether the text constructs particular linguistic and semantic fields around particular parts of the text. Specific terms clearly occur in isolated contexts. The octopus rarely returns; most of Roger's narrative is centred around his pairing and unpairing with Jessica; Byron the Bulb is far out in his own diegetic layer with distinct terms that rarely recur.

Other terms, though, seem scattered across the Zone of the text. As an initial hypothesis that I need to explore much more: it could be that many of the isolated action segments of the text, to which critics have turned their thematic and historical attentions, may share common linguistic cores (semantic fields) with many other parts of the text. This might begin to contribute to their ultimate connectedness within the novel.