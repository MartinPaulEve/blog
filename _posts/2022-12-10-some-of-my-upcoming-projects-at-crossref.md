---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2022/12/10/some-of-my-upcoming-projects-at-crossref
date: 2022-12-10
doi: https://doi.org/10.59348/fnt1b-s2x58
roguescholar: https://rogue-scholar.org/records/ghhcc-wek39
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lyi5jsk2a
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: Some of my upcoming projects at Crossref
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lyi5jsk2a"
categories:
- Scholarly Communications
- Digital Preservation
---

As I posted a while ago, from January 2023 [I will be working at Crossref](https://eve.gd/2022/08/26/moving-on-my-infrastructural-turn/) while retaining my university Professorship. I wanted, here, to outline a few of the projects that I hope to work on once I get started there. I should say upfront: I am afraid there is no time estimate on these and we can't guarantee to prioritise any particular project. But if there is one that stands out to you, do let me know, as this serves as a useful community gauge.

## Project "Op Cit"
This is a really great one.

What is a DOI? Some people think it's a link that resolves, but really it's part of a complex social agreement for digital preservation. Indeed, the PILA agreement, that organsiations sign in order to be able to issue Crossref DOIs, contains a commitment to preservation. It is this social agreement that yields the persistence of the link, because if the original content disappears, the link can be redirected.

Yet what proportion of the content assigned a DOI is actually preserved? Many smaller publishers, in particular, may not actually have good preservation systems in place. Is this something with which Crossref could help?

What if we checked, on deposit and periodically thereafter, on the preservation status of this material? What if _we_ ensured that, when we received a full-text deposit, the object in question was stored somewhere? This would allow us to heal broken DOIs and ensure the that the preservation contract is always enforced.

There's a heap of social work around this -- mostly to make sure that we get the preservation aspects right -- but this could create a much more robust DOI ecosystem if it works. I wonder, also, whether we might use the Keepers Registry as a potential data source? Certainly, I need to read [their license](https://portal.issn.org/content/license-contract) carefully...

## Official APIs
There are some really great unofficial APIs for Crossref's systems. I want to make them official and graduate them to production.

This will involve taking the existing APIs, ensuring they are fully documented and using all best practices, making sure we credit the original authors, and writing enough material to ensure that we don't introduce breaking changes in the future.

I also want to use this opportunity to think through extensions that we might make to existing APIs. For instance: a sampling framework is under development. Easy shortcut programmatic access to this type of functionality will enhance research possibilities for the database.

## Data wrappers and availability
Every year -- and at periodic intervals for updates -- Crossref releases a large public data file (156.5GB this year) of its entire dataset.

This dataset is, ahem, slightly tricky to use. To give an idea of the current structure, its a series of files like this: 14933.json.gz 16657.json.gz 18380.json.gz  20102.json.gz 21827.json.gz 23550.json.gz 25274.json.gz 287.json.gz 4593.json.gz. Indeed, it's not particularly user friendly and there is [guidance on how to use the dump](https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-public-data-files-and-plus-snapshots/).

I think it would be good if we provided a standard implementation of a wrapper for this dump and this would be a good project. I could even imagine things like FUSE filesystems that wrap the data for general FS readability (although one of the reasons that the data is packaged in this way is that most filesystems do not handle very large directories very well at all).

There's also the issue of availability, though. At the moment, we distribute this file via a torrent. Some administrative centres block torrent downloads, fearing piracy. So we need to think through alternative dissemination mechanisms. Could IPFS work? What about an Amazon S3 bucket with reverse charges?

Could we also reconsider or expand the available formats here? JSON-L, Parquet, or even SQLite?

## Corpus builder
I've already mentioned the sampling framework that is under development. This, I believe, allows for slicing across either the entire Crossref corpus or by publisher. The question then becomes: how many ways can we cut the cake? What other sub-corpuses might researchers want to pull from our dataset? How could we make this possible without massive computational resource consumption?

## Reference matching stuff
Linked to the dataset availability and wrappers, could we play around with some lightweight indexing tools, like Meilisearch, to see whether we can achieve better fulltext reference matching?


In any case, some initial ideas that I can't wait to get hacking on...