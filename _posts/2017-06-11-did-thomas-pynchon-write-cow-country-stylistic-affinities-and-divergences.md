---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2017/06/11/did-thomas-pynchon-write-cow-country-stylistic-affinities-and-divergences
date: 2017-06-11
last_modified_at: 2026-09-06
doi: https://doi.org/10.59348/834je-wsz88
roguescholar: https://rogue-scholar.org/records/r8v9g-wwv59
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mabdqni2h
layout: post
title: Did Thomas Pynchon write Cow Country? Stylistic affinities and divergences
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mabdqni2h"
categories:
- Thomas Pynchon
- Digital Humanities
kcworks: https://works.hcommons.org/records/hvr4r-1yp29
references:
- author: Nate Jones
  date: '2015-09-10'
  title: Did Thomas Pynchon Write a New Secret Novel That He Published Under a Psuedonym to Punk the Literary Press? (Probably Not)
  type: NewsArticle
  url: http://www.vulture.com/2015/09/pynchon-probably-did-not-write-a-secret-novel.html
  isPartOf:
    name: Vulture
    type: Periodical
- http://link.springer.com/10.1007/978-3-662-44952-3_13 # Stolerman chapter on computational forensic stylometry accuracy
- http://thomaspynchon.com/thomas-pynchon-did-not-write-cow-country/ # thomaspynchon.com: Tim Ware on Pynchon not writing Cow Country
- https://doi.org/10.1093/llc/fqn003 # Burrows Delta stylometry method article in LLC
- author:
  - Stefan Evert
  - Fotis Jannidis
  - Thomas Proisl
  - Thorsten Vitt
  - Christof Schöch
  - Steffen Pielström
  - Isabella Reger
  title: Outliers or Key Profiles? Understanding Distance Measures for Authorship Attribution
  type: ScholarlyArticle
  url: http://dh2016.adho.org/abstracts/253
- https://doi.org/10.1093/llc/17.3.267 # Burrows on authorial fingerprints LLC article
- https://sites.google.com/site/computationalstylistics/stylo # Stylo R package for computational stylistics
- author: Alex Shephard
  date: '2015-09-12'
  title: The Hunt for a Possible Pynchon Novel Leads to a Name
  type: NewsArticle
  url: http://www.newrepublic.com/article/122802/thomas-pynchon-didnt-write-cow-country-aj-perry-probably-did
  isPartOf:
    name: The New Republic
    type: Periodical
---

In mid-2015, Art Winslow caused something of an online furore when he suggested that the pseudonymously-authored novel by “Adrian Jones Pearson”, _Cow Country_, was, in fact, a work by Thomas Pynchon. A full-blown argument then erupted when this was countered by Nate Jones and Pynchon's own publisher. Indeed, [Penguin thundered](http://www.vulture.com/2015/09/pynchon-probably-did-not-write-a-secret-novel.html): “[w]e are Thomas Pynchon's publisher and this is not a book by Thomas Pynchon”.

To be frank, Winslow's evidence was slight and bound to irritate fans and critics alike. [He argued](https://harpers.org/blog/2015/09/the-fiction-atop-the-fiction/) that the author biography of _Cow Country_ pointed to a recluse; someone who didn't like to be in the limelight, a J.D. Salinger. From this, he leapt to the conclusion that Thomas Pynchon was a likely candidate. The second piece of evidence that Winslow furnished was that the novel is a work of metafiction; another potential Pynchonian connection. Winslow also evaluates the dismantling of binaries within _Cow Country_, the humorous character names that abound throughout (we have "Dr Felch"), apparent running Pynchon-like gags and more. For Winslow, “[t]he off-kilter sensibility one sees in the work of both [authors] would not be […] easily 'replicable' by another”.

_Cow Country_ itself is an amusing-enough read. It's a campus novel set in a backwater Community College and the trials of the newly arrived educational administrator, Charlie. This hapless individual is set to head the College's re-accreditation drive, which, to be frank seems a big ask. For instance, the College's new staff orientation event consists of the castration of a calf as an exercise in team building. You get the idea.

In this post, I turn to a set of computational authorship attribution methods to examine the stylistic properties of Pynchon's novels in comparison to _Cow Country_. These methods consist of statistical analyses of the most frequent words used by Pynchon as opposed to Pearson and the order in which they occur. This may sound extremely dry and of little worth – counting words does not always go down well in literary circles – but, in fact, these techniques have been shown to be highly accurate under specific circumstances. Indeed, at the time of writing, [according to Ariel Stolerman](http://link.springer.com/10.1007/978-3-662-44952-3_13), computational forensic stylometry “can identify individuals in sets of 50 authors with better than 90% accuracy, and [can] even [be] scaled to more than 100,000 authors”.

##Pynchon's Style and Stylometry

[Tim Ware took the existing critiques](http://thomaspynchon.com/thomas-pynchon-did-not-write-cow-country/) of the “Pynchon as author” further and published a list of stylistic and thematic traits that he felt misaligned _Cow Country_ with Pynchon's writing. Namely, that:

* Although there’s always a first time, Pynchon has never written in the first person, and _Cow Country_ is in the first person.
* Right out of the gate, _Cow Country_ sounds nothing like Pynchon… none of his style, grace, wit, voice, subtlety.
* Pynchon has his own work agenda, with a pipeline of novels in various states of completion. That he would take the time to write a “spoof” on the publishing business and exagerated importance given to author biographies — a work of 540 pages, no less — is silly. Let’s just say he has bigger fish to fry…

The part-of-speech analysis that Ware provides is simple but sound: Pynchon has, indeed, never written a novel in the first person. Although this could, then, be used as a rationale for a pseudonym. When Ware gets onto the line that it “sounds nothing like Pynchon”, though, we are in more interesting territory. What does it mean to say that an author “sounds like” another or that there might be a characteristic essence of a writer's “style”? What, even, do we mean by the term “style” and what is its relationship to thematics? How is a writer's language inflected by the topics about which he or she writes?

Despite the many criticisms of stylometry, into which I won't delve here, and in order to determine whether Pynchon writes like Pearson, from the perspective of computational stylometry, I used a method called Burrows's delta. With apologies for a brief mathematical deviation, Burrows's delta consists of two steps to conduct a multivariate statistical authorship attribution. First of all, one measures the most-frequent words that occur in a text and then relativizes these using a “z-score” measure. A z-score measurement is basically asking: “by how much does a word's frequency differ from the average deviation of the other words?” So, the first thing that we would calculate here is the “standard deviation” of the the entire word set. A standard deviation means the square root of the average of the squared deviations of the values from the average. Or, in other words: work out the average frequency with which words occur in a text, then work out (for each word) how many more or less times that word occurs relative to the average, square this and add up all such deviations, then divide this by the number of words, then square root the result. To get the z-score, we next take an individual word's frequency, subtract the average (mean) frequency, and divide this result by the standard deviation of the whole set.

Once we have a ranked series of z-scores for each term, the second operation in Burrows's delta is to calculate the difference between the words in both texts. This means taking the z-score of, say, the word “the” in text A and subtracting the z-score of the word “the” in text B. Once we have done this for every word that we wish to take into account, we add all of these differences together, a move that is the mathematical equivalent of taking the “Manhattan distance” (named because it moves in right angled blocks like the city of Manhattan, rather than going “as the crow flies”) between the [multi-dimensional space plots of these terms](https://doi.org/10.1093/llc/fqn003). In Burrows's delta, the smaller this total addition of differences is, the more likely it is that two texts were written by the same author.

Burrows's delta has been seen as a successful algorithm for authorship attribution for many years, as [validated in several studies](ttps://doi.org/10.1093/llc/fqr031). It is, mathematically speaking, relatively easy to calculate and seems to produce good results. However, it is not entirely known why the delta method is so good at clustering texts written by the same author, although [recent work](http://dh2016.adho.org/abstracts/253) has suggested that such a “text distance measure is particularly successful in authorship attribution if emphasizing structural differences of author style profiles without being too much influenced by actual amplitudes”, as does Burrows's delta.

Yet, Burrows himself was always cautious about what he was doing. When writing of “authorial fingerprints”, for example, [Burrows noted](https://doi.org/10.1093/llc/17.3.267) that “we do not yet have either proof or promise” of the “very existence” of such a phenomenon. Burrows also points out that, “[n]ot unexpectedly”, his method “works least well with texts of a genre uncharacteristic of their author and, in one case, with texts far separated in time across a long literary career”.

##Does Pearson Write Like Pynchon?

So, when using this method, do Thomas Pynchon and Adrian Jones Pearson write in similar ways? I am afraid to say that the answer is a fairly conclusive “no”, as you might have already concluded yourself. I first explored this using the aforementioned method using single words, sets of two-words (bigrams), and sets of three words (trigrams) inside the R programming language's “[Stylo](https://sites.google.com/site/computationalstylistics/stylo)” package. I then clustered these using 30 to 100 words (and all numbers of words in between: e.g. 31 words, 32 words etc.) and taking the most common result in 80% and 90% of cases.

Admittedly, when using only single words, there is a similarity between Pynchon and Pearson that seems alarming. Note that I have also added Don DeLillo's corpus here in order to provide a foil for the system and so that we can gauge the accuracy of its profiling techniques. At an 80% consensus between all word frequencies, this algorithm believes that _Cow Country_ is most similar, linguistically, to _Bleeding Edge_, _Gravity's Rainbow_ and _V._ At 90% there is very little consensus and the algorithm does not correctly cluster any of the Pynchon works as significantly close to one another.

<img src="/images/1-gram-30-100MFW-Consensus0.8.png" style="width:100%;" alt="1 Gram 30-100 MFW 80% consensus"/>

Things do, though, get a bit more interesting when we move on to bigrams and trigrams. In the bigram and trigram models – that's sets of two words in a row that authors share with each other along with the ways in which these tropes are ordered – most of Pynchon's novels are tightly clustered together, indicating a distinct writing style. The same goes for DeLillo. However, _Cow Country_ does not cluster with these other authors. This points towards the likely probability of a different author being responsible for this novel.

<img src="/images/2-gram-30-100MFW-Consensus0.8.svg" style="width:100%" alt="2-Gram 30-100 MFW 80% consensus"/>

Indeed, [others have speculated](http://www.newrepublic.com/article/122802/thomas-pynchon-didnt-write-cow-country-aj-perry-probably-did), based on hints dropped by Steven Moore, that the actual author of _Cow Country_ is one A.J. Perry. Perry is the author of two other books, but lists himself as the author of three on his website. I took one of these books and dropped it into my authorship profiling tool.

Whether using single words, bigrams, or trigrams, I received exactly the same result in this case. Perry's _Twelve Stories of Russia, A Novel I Guess_ published in the year 2012, markedly clusters with _Cow Country_. Note also that, once Perry is thrown in, Pynchon and DeLillo are clustered almost entirely accurately and distinctly by this algorithm.

<img src="/images/2-gram-30-100MFW-Consensus0.9.png" style="width:100%" alt="2-Gram 30-100 MFW 90% with Perry Thrown In"/>

I'm going to draw this to a close now and I suspect one of the criticisms to be levelled at this post is that I am probably telling you exactly what you knew and believed before I presented any of this work. Namely, that it is extremely unlikely that Thomas Pynchon is the author – or at least the sole author – of the novel _Cow Country_. Using Burrows's delta, there are some similarities in single word choices, but the syntactic inflection of Pynchon's writing is very different at the level of two and three -word groups. I would like, ideally, to release the data underlying this post. But the cleanup that I'd need to get to the point where that is wholly possible doesn't seem worth it. Certainly, these methods have their weaknesses, but combined with the sociological investigations into authorship that others have already conducted, I believe it is highly likely that A.J. Perry is the author of _Cow Country_. But, as Pynchon puts it in _Bleeding Edge_: “it’s code’s all it is”, for sure.