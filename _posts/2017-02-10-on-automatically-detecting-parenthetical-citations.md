---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2017/02/10/on-automatically-detecting-parenthetical-citations
date: 2017-02-10
doi: https://doi.org/10.59348/hqs21-cxk70
roguescholar: https://rogue-scholar.org/records/wbcnz-c8e02
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7magzuue2t
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: On automatically detecting parenthetical citations
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7magzuue2t"
categories:
- Publishing Technology
- Programming
kcworks: https://works.hcommons.org/records/p8xcr-05z34
references:
- https://github.com/MartinPaulEve/meTypeset # meTypeset GitHub repository for typesetting tool
---

One of the things that we have to do in [meTypeset](https://github.com/MartinPaulEve/meTypeset) is to capture parenthetical citations. These range in styles, but the following are good examples:

* Some text (Martin Eve, p. 45)
* Eve notes (345).
* Eve notes (p. 345)
* A great thing (Alex, P. 45)
* Here is one of them: (Silva, Rodrigues, Oliveira, & da F. Costa, 2013)
* Eve says (Eve 54)
* Eve says (Eve, 54)

However, there are also often cases where the logic looks quite different:

* As I Note (AIN)
* The Large Hadron Collider (LHC) is great (Eve, p. 3)

How can we distinguish between acronyms, asides, and genuine parenthetical citations?

There are also some other challenges. [Some people](https://en.wikipedia.org/wiki/List_of_people_with_lower_case_names_and_pseudonyms) have names that are written in lowercase (taken here [from Wikipedia](https://en.wikipedia.org/wiki/List_of_people_with_lower_case_names_and_pseudonyms)):

* eden ahbez, American musician
* bill bissett, Canadian poet
* danah boyd, American scholar
* e e cummings, American poet
* mc chris, American rapper
* Arthur fforde, British solicitor
* Charles ffoulkes, British historian
* Rose ffrench, 1st Baroness ffrench, Irish peer
* Michael ffrench-O'Carroll, Irish politician
* brian d foy, American magazine publisher
* debbie tucker green, British playwright
* jack green, American critic
* dream hampton, American filmmaker
* bell hooks, American feminist
* k.d. lang, Canadian singer
* Conrad O'Brien-ffrench, British military officer
* ruth weiss, American writer

How can one distinguish between "This led to greater possibilities to resistance (hooks)" and "This led to greater possibilities to resistance (ohms)"? We have the additional challenge that checking for acronym-like behaviour is unlikely to succeed; authors make typos etc. that are easy to spot by eye but difficult to judge computationally in a wide range of situations.

What we've been doing so far is pulling out text between brackets that doesn't look like a mathematical expression and then seeing if we can find a corresponding bibliographic entry. This is prone to many bugs and doesn't actually work very well. In reality, many documents erroneously end up with parenthetical asides that are within a ref tag but that are unlinked as we're unable to parse the entry.

To begin to solve this problem more thoroughly, I wrote the following regular expression:

    (?:\((?P<text>((?:[A-Z]{1}[a-z\s,\.\d\;&]+)*|(?:p?P?\.?\s?\d+))|.+\<ref\s.+)\))

This does several things. It matches a set of parentheses that contain either:

1. A set of words that are all capitalised on the first letter only, followed by a series of other words, numbers, or special characters.
2. A set of numbers following an optional p. or P.
3. It catches cases where a URL is included within the brackets so that we can match them.

The next thing to do, I think, is to embed the above authors as special cases that we know may occur and that must be handled separately. There is no, so far as I can see, easy way to determine whether we're referring to bell hooks or other arbitrary lowercase words without the specificity of her name being encoded. I had thought about whether we could do some keyword scanning/topic modelling of documents to determine likely authors/parenthetical asides, but this then gets very complicated.

If anyone has any better ideas for how to distinguish between various use cases/false positives here, please do open an issue on the meTypeset page.