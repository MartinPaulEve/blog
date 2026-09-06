---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2019/06/01/what-size-should-my-music-studio-be
date: 2019-06-01
doi: https://doi.org/10.59348/q50f8-zec39
roguescholar: https://rogue-scholar.org/records/aw9b2-kst18
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m6vsz3y2h
image:
  feature: music.png
layout: post
ogImage: images/music.png
title: What size should my music studio be?
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m6vsz3y2h"
categories:
- Music
- Programming
kcworks: https://works.hcommons.org/records/v59p5-zaq94
references:
- title: acousticsize
  type: SoftwareSourceCode
  url: https://github.com/MartinPaulEve/acousticsize
  isPartOf:
    name: GitHub
    type: WebSite
---

In Everest, F. Alton, and Ken C Pohlmann, _Master Handbook of Acoustics_ (New York: McGraw-Hill, 2009), p. 247, a range of room ratios are listed to achieve optimal modal distributions using the Bolt range and a set of external sources. In other words, this addresses the question: what size should I make my room to achieve the best even distribution of sound throughout?

In order to facilitate these calculations, I have written an open-source program, [acousticsize](https://github.com/MartinPaulEve/acousticsize), that will let you calculate room dimensions that fall within the Bolt range using these secondary sources, based on a height input.

So, for example, if you had an internal room height dimension of 2m, you could do:

~~~~

python ./acousticsize.py 2
[Sepmeyer B] 
[Height]: 2
[Width]: 2.56
[Length]: 3.08

[Sepmeyer C] 
[Height]: 2
[Width]: 3.2
[Length]: 4.66

[Louden D] 
[Height]: 2
[Width]: 2.8
[Length]: 3.8

[Louden F] 
[Height]: 2
[Width]: 3.0
[Length]: 5.0

[Volkmann] 
[Height]: 2
[Width]: 3.0
[Length]: 5.0

[Boner] 
[Height]: 2
[Width]: 2.52
[Length]: 3.18
~~~~