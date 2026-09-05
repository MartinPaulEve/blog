---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2023/07/26/whats-the-point-of-having-open-scholarly-infrastructures-and-how-do-we-test-their-resilience
date: 2023-07-26
doi: https://doi.org/10.59348/smag6-td951
roguescholar: https://rogue-scholar.org/records/kpkwh-1ka66
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7ly4cktq2i
image:
  feature: oa.png
layout: post
ogImage: images/oa.png
title: What’s the point of having open scholarly infrastructures and how do we test
  their resilience?
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7ly4cktq2i"
categories:
- Scholarly Communications
kcworks: https://works.hcommons.org/records/p071q-dde52
references:
- https://openscholarlyinfrastructure.org/ # Principles of Open Scholarly Infrastructure site
- https://www.crossref.org/blog/outage-of-october-6-2021/ # Crossref blog post on October 2021 outage
---

It is sometimes easy, when discussing openness, to get bogged down in the technical weeds. People often want detail and specifics: what open license should I use? Precisely how much revenue do I need to keep in reserve safely to wind-down an organization? When does advocacy become lobbying?

Yet these specifics, while they can be important, may also distract us from stepping back and understanding why we are building open scholarly infrastructures. Is it just “open” because everyone (policymakers) has decided that “open” is a virtue? What benefits are there in infrastructure being “open” – and what, even, do we mean by that?

For me, the fundamental meta-principle, or ideal, that underpins [POSI (the Principles of Open Scholarly Infrastructure)](https://openscholarlyinfrastructure.org/) is forkability and persistence. Taken on aggregate and implemented, an organization that signs up for POSI should be duplicable. That is: I should be able, as a reasonably technically competent individual, to acquire all the components of a POSI-posse signatory, and rebuild/resurrect their technical architecture.

Certainly, this can be a scary proposition to those unschooled in thinking this way. Might not other organizations just usurp us if we do this? What’s to stop someone else just stepping in and re-selling all of our data? However, to think like this is to under-estimate the social aspects of scholarly infrastructural organizations. Certainly, the technology is important. But perhaps even more crucial are the communities and economic models that support such organizations. To effect a hostile fork would require such a community critical mass that we can safely hazard that the original organization was doing something very wrong in the first place.

But why do we want this “forkability”? The simple answer, as with many things at Crossref, where I work, is: persistence. The scholarly infrastructures on which we depend for (say) linking and metadata resolution must continue to exist and there must be mechanisms for their ongoing operation. POSI is designed to allow an arbitrary third-party entity to continue the operation of an infrastructure in the event of the original organization’s demise – or in cases where the original organization might be acting against the wishes of the community.

A valid question is: would someone take it on? Who would continue the operation of a POSI infrastructure provider that failed? Well, the benefit of the principles is that we don’t have to know that ahead of time. Downstream re-use, without permission, allows anybody who needs it to take on the infrastructure. Of course, it might be a good idea to have an organization that agrees to take on the service in advance of failure, rather than leaving it to chance. But POSI gives greater certainty that an infrastructure can be continued.

In another, forthcoming, post, I will write something about self-“audits” of POSI, which have become all the rage in recent days. And it can, of course, be useful to measure yourself up against each of the points in the declaration. However, without care, such audits can descend into bean counting. Getting lost, once more, in the technical weeds with which I opened.

At the end of the day, though, there is a single test that can determine whether you have achieved POSI compliance, adhering to the overarching meta-principle: can someone fork you? If not, then you are not there yet (which is OK).

A point that disturbs me, though, is that we have never tested this forkability on any of the key scholarly infrastructures. Wargaming simulated disasters is common practice in organizations. At the Open Library of Humanities, we simulated a total systems failure and resurrected everything from backup. Crossref has, in the past, found that even massively redundant systems [can go wrong](https://www.crossref.org/blog/outage-of-october-6-2021/) if not tested.

It’s also highly possible to fulfil all the POSI points in a way that doesn’t satisfy the forkability meta-principle. You can make all your code openly available, for instance, under an open license… but it can be such a mess or so poorly documented that nobody outside of your organization could ever spin it up. Likewise, you might comply with the spirit of POSI by licensing your data openly, but under conditions that limit who could ever resurrect the project (e.g. CC-BY-ND, CC-BY-NC, or, even, CC-BY-SA – even though I am usually a fan of ShareAlike licenses). You could also, for example, not provide a build environment for your software. The list of ways in which you can be “open in name only” goes on.

So what I’d really like to see from here is thought from infrastructure organizations on what such an external test would look like (for instance: the ease of forkability is also a factor here and it’s not just a binary can it/can’t it be forked). 

But I’d also love to see a funder step up to underwrite such forkability testing. This would not be that expensive in each case and organizations could say when they think they are ready. Yet until we conduct this acid test, with an external agent stressing the system for real, much of the benefit of POSI is hypothetical. This is the way we can ensure the persistence of our scholcomms infrastructures.