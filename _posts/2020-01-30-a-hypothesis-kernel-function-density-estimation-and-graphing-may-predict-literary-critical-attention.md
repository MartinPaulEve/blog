---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2020/01/30/a-hypothesis-kernel-function-density-estimation-and-graphing-may-predict-literary-critical-attention
date: 2020-01-30
doi: https://doi.org/10.59348/tvj8v-exb52
roguescholar: https://rogue-scholar.org/records/xnmkq-6qr42
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m6jezwv2f
layout: post
title: 'A hypothesis: kernel function density estimation and graphing may predict
  literary critical attention'
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m6jezwv2f"
categories:
- Digital Humanities
- Thomas Pynchon
kcworks: https://works.hcommons.org/records/sdwh3-3j453
references:
- title: 'GitHub - davidmcclure/textplot: (Mental) maps of texts with kernel density estimation and force-directed networks.'
  type: SoftwareSourceCode
  url: https://github.com/davidmcclure/textplot
  isPartOf:
    name: GitHub
    type: WebSite
---

This is really speculative, but today I returned to David McClure's [excellent and fun TextPlot tool](https://github.com/davidmcclure/textplot). A type of topic modelling (but not LDA), McClure explains his [Bray-Curtis dissimilarity mapping in a separate post](http://dclure.org/essays/mental-maps-of-texts/) but essentially what is being measured here is the interconnectedness and proximity of various terms within a network graph. In texts with distinct episodic structures, this means that the graphs that are produced by this method cluster abstract terms centrally within the network and push distinct linguistic clusters to the edges. I hypothesize that these peripheral nodes represent the episodes that will receive literary critical attention.

This hypothesis is based on [my modelling of the extremely episodic _Gravity's Rainbow_](https://eve.gd/2015/06/07/visualizing-gravitys-rainbow/), which highlights the following episodes, all studied extensively in the secondary literature:

* Byron the Bulb
* The encounter between Tchitcherine and Enzian
* The Herero back story
* The Roger-Jessica romance
* Brigadier Pudding (!)
* Pointsman
* Leni-Pokler-Weissman and the abandoned theme park
* The octopus abduction
* The Anubis boat scene and its associated sadomasochism
* Der Springer
* Rocketman's Potsdam Pickup
* Major Marvy
* Bodine and Krypton on the John E. Badass

There are some false positives (instances that appear isolated but that are not that widely remarked upon). The clearest of these to me is the minor character Gwenhidy, who here sticks out a mile but isn't really that extensively covered in the secondary literature.

Perhaps this is unremarkable: critics are drawn to exceptional scenes and language in texts. What I wonder is this: does this have potential predictive power? If you gave me a text now, in the present, that would go on to achieve a wide level of literary critical commentary (good luck identifying that text), could I produce a list of terms in distinct episodes that would likely form the basis for future literary critical attention? It is possible.

Perhaps this hypothesis is just wrong. A way of testing it could be: 

1. Select X number of novels that have received previous literary critical attention;
2. Compute the nodes that are force-directed to the edges in the graph;
3. Produce a set of topics of interest;
4. Systematically read the secondary literature, noting which episodes are mentioned. Ideally this should be conducted by a separate party to the person who produced an above list of predicted episodes;
5. Ascertain whether the episodes at the edge of the graph receive the most attention.

It would also be good to know: which episodes are mentioned but do not stand out from these graphs? Are there episodes at the edge of the graph that do not receive attention? This would all contribute to our understanding of foregrounding in texts.