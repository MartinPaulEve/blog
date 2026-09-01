---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2018/08/07/open-source-patents
date: 2018-08-07
doi: https://doi.org/10.59348/658d6-xmm51
roguescholar: https://rogue-scholar.org/records/n0xdx-tm239
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m7pgb2b2a
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: Institutional Cultures, Patents, and Open-Source Software for Open Access
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m7pgb2b2a"
categories:
- Copyright and Licensing
- Publishing Technology
---

As you may know, the Centre for Technology and Publishing at Birkbeck publishes and maintains a piece of open-source software for journal publishing called [Janeway](https://github.com/BirkbeckCTP/janeway/). This software is licensed under the AGPLv3.

We chose this license for several reasons, but the most important was that we wanted strong CopyLeft protection, including for server-side usage, on this software. Other journal publishing software has been used extensively by for-profit third parties who refuse to contribute their modifications back into the open ecosystem. We do not wish to develop software that can be made subject to corporate, for-profit enclosure. Given recent acquisitions by Elsevier, this seems all the more important at this time. This seemed, to us, to offer the best deal for the community who pursue open access, as it is advocated for inside many academic libraries.

Imagine our dismay this week, then, when a big (and I mean _very_ big) institution -- one that is very supportive of open access and that does many, many good things around this field -- told us that it was unlikely to be able to contribute code to Janeway because of our license choice. The reason? It's to do with the patent grant clause in the license.

Essentially, this university was in a situation where it holds a sizable portfolio of (software) patents. Employee clearance to work on projects is conducted on the basis of [a risk matrix](https://security.ucop.edu/resources/open-source-software-licensing.html). The situation that the want to avoid is as follows:

1. Someone patents something somewhere in the university.
2. The university enters into an exclusive agreement with someone else for the patent.
3. A different employee contributes code/functionality to Janeway that is covered by the patent, violating the previous exclusive agreement.
4. The institution is liable.

It is, therefore, the patent grant aspect of the AGPL3 to which the University objects. They want indemnification for their employees making a mistake.

I have a number of gut reactions to this. The first is that we should not encourage anyone to file and to license software patents. They are a [harmful practical and intellectual development](https://www.gnu.org/philosophy/software-patents.en.html).

More importantly, though, were a set of other thoughts:

1. The patent grant clause in the GPL is there for our protection. If we changed the license and an institution behaved as above anyway, committing code that happens unwittingly to be the subject of an exclusive patent license owned by your institution, we would end up being the liable party and our ability to use and distribute the software would be compromised. If parties can commit code to which they or their institution owns patents and that they have licensed exclusively elsewhere, we cannot and should not end up being the liable party for that behaviour. If it is felt that this behaviour is unlikely, though, then I do not understand why this license is deemed high risk.
 
2. Other licenses, such as MIT (which is deemed "low risk"), contain implied, or even [express, patent grants anyway](https://opensource.com/article/18/3/patent-grant-mit-license) (and thus do not solve the problem), while they do not give us the CopyLeft protections set out above. This policy does not seem to have correctly evaluated the license on this front.

3. Libraries that want to advocate for openness in research practice and software should be campaigning against their institutional policies on software patents in this area. Institutions should not hold them, they should not license them, and they should not enforce them. For, if doing so forces open-source projects off licenses such as the AGPL3 and onto more liberal licenses, platform projects are being re-opened to for-profit enclosure and exploitation, against the explicit stated desires of many academic research librarians. The AGPL doesn't stop for-profits using our code -- it just ensures that they have to contribute any changes back into the open, so they can't make their offering a distinct product with closed advantages.

It feels to me, ridiculous, that a large university should insist, if its staff participate in open-source software work, that the open-source software bear the risk of the institution messing up. Because that's basically what it is: an indemnity clause against their own inability to manage their software patent portfolio. This is frustrating, to say the very least.

All that said, we really _want_ community and institutional participation. I think the actual risks are negligible. Most functionality in publishing platforms has prior art. If there is something radically new contributed, we'll do a patent search. For that reason, we are likely to change the licensing terms on Janeway to the AGPL version 2 in the near future.