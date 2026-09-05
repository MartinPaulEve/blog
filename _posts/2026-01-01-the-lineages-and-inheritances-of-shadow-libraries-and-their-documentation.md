---
archive: https://wayback.archive-it.org/22123/20241101171236/https://eve.gd/2026/01/01/the-lineages-and-inheritances-of-shadow-libraries-and-their-documentation
date: 2026-01-01
doi: https://doi.org/10.59348/1mrf2-35g29
kcworks: https://works.hcommons.org/records/pm6ta-dxp10
roguescholar: https://rogue-scholar.org/records/w9qkr-a2d51
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lvdokvd2s
image:
  credit: Jakob Rosen on Unsplash
  creditlink: https://unsplash.com/@jakobnoahrosen
  feature: pirate.jpg
  title: Pirate skull
layout: post
ogImage: images/pirate.jpg
title: The Lineages and Inheritances of Shadow Libraries and their Documentation
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lvdokvd2s"
categories:
- Piracy and Shadow Libraries
- Digital Preservation
references:
- https://dhq-static.digitalhumanities.org/pdf/000587.pdf # Eve DHQ article on shadow library metadata
---

Shadow libraries, that is, illegal massive repositories of books of all kinds, are of course prone to takedowns by police and disappearance from the internet. In recent days, one of the most prominent shadow libraries, Library Genesis (libgen), was taken down and its archive removed from public consumption.

> This is a post about pirate libraries and their technologies and documentation. Before we go any further, I wish to clarify that I am not endorsing any of these sites and am certainly *not* involved in any of their operations. I am merely interested in them as a scholarly publishing phenomenon. To write this post, I had to look at the Anna's Archive metadata set.

> In this post, I discuss how, with every takedown of a pirate archive that occurs, it becomes harder and harder to resurrect a catalogue with a concrete lineage. Therefore, I posit, it is not clear who will have the resources to continue pirate systems like Anna's Archive, if it is taken down, which I suspect it will be.

The takedown of LibGen was no massive shock. Indeed, several projects were already continuing LibGen's legacy. On the one hand, the LibGen+ system has a different archival strategy going forward, but nonetheless continues the name of the original Library Genesis. On the other hand, Anna's Archive is a prominent new hub to which scholars without access are flocking to obtain books for free.

Anna's Archive has [extensive documentation](https://software.annas-archive.li/AnnaArchivist/annas-archive) that details how to get a copy of the archive running locally, provided you have several hundred terabytes of storage space available. It even has [documentation for those who wish to conduct metadata analysis](https://github.com/RArtutos/Data-science-starter-kit-Enhance/) for scholarly purposes of the books in the archive. [Importing the metadata into a local Anna's Archive system](https://software.annas-archive.li/AnnaArchivist/annas-archive/-/blob/main/data-imports/README.md) is supported and well documented. Although, as the documentation notes, it can take up to a week to run on a fairly high-end machine.

But what is the relationship between Anna's Archive and Library Genesis? Let's say that someone had been downloading the entirety of Library Genesis archives by torrent and wanted to know who is continuing this project. After all, one of the rationales put forward by shadow libraries is that they are preservation systems. So, when distributing material, you would expect a strong lineage of continuity. That is: what is the logical sequential next step for somebody to download the next tranche of books? This basic question is: what happens when shadow libraries die?

In reality, the answer is that no single successor site has continued LibGen’s torrent archive in a clean, authoritative, linear way. Instead, LibGen’s torrents, IDs, and metadata have fractured into multiple partially overlapping lineages, with different projects inheriting some parts of LibGen’s corpus and diverging in how they expand and describe it.

After LibGen went down it seems that there was a fragmentation of its archive. The LibGen+ mirrors retain the legacy IDs and tables but do not continue the legacy. Also, in the LibGen system, metadata continues to mutate while the torrents and the files within remain static. This allows for a bit by bit improvement of such metadata, [as I have argued elsewhere](https://dhq-static.digitalhumanities.org/pdf/000587.pdf) [PDF link].

Anna's Archive, conversely, is the closest thing to a meta-successor for LibGen. It aggregates LibGen, SciHub, zLibrary, Internet Archive, and others. It then normalizes metadata across sources and tracks provenance explicitly. It indexes torrents, but does not preserve LibGen's original torrent lineage as a single expanding series. Anna's Archive is therefore a union catalogue with a reconciliation layer.

The cataloguing system at Anna's Archive is complex and, to my mind, poorly documented. Let us say that someone wants to understand how to resolve from metadata to a file (a common operation). It turns out there's an IA metadata JSON with author, title, date etc. and a VERY confusing set of extraneous metadata that are not needed. However, to then find the file, you have to grep inside a 2gb plain-text JSON-L file, which yields the data directory and filename of the decrypted PDF that correlates to the ACSM. The MD5 does NOT correlate from the metadata record to the file record, which led me down a blind alley. It's only the ia_id field that links them.

Anna's Archive is at *enormous* risk of legal takedown. It is brazen in what it's doing, completely openly violating copyright. While this does make it perhaps the biggest archive of digital books in the world, it has recently also downloaded 300 terabytes of Spotify data for "preservation". This will make it an even bigger legal target. On top of all this, the site takes donations or even payments in return for faster download slots. This is usually a HUGE "no-no" that is just asking for trouble. That is, Anna's Archive could be deemed to be selling the copyrighted material that it has pirated. There is little doubt in my mind that at some point the authorities will come for Anna's Archive and they will take it down. I suspect that "Anna", whomsoever they may be, will receive a substantial prison sentence.

So what does it mean for pirate archives that the metadata formats of Anna's Archive are so hard to understand and are so poorly documented? To get any sense of how the archive works one has to [look at the code](https://software.annas-archive.li/AnnaArchivist/annas-archive/-/blob/main/SCRAPING.md) and read the metadata to understand how IDs are used, and to grok to what MD5 sums refer. (Hint: it's not always what's in the files folder and metadata.) There is no doubt also in my mind that even when Anna's Archive is taken down, others will flock to resurrect its work and continue a pirate legacy of the site. But they will have a tough time as the site grows.

Pirate archives continue to fascinate me in their brazen activity in some ways but also disregard for authorship and intellectual property ownership. However, as they become more sophisticated in their cataloging processes, as I have discussed in this post, the challenges of resurrecting such sites when they are taken down becomes greater each time, particularly if the documentation is not great.

Furthermore, the infrastructure that is required to run a local copy, as I said, several hundred terabytes, is becoming more and more expensive. To get that kind of storage, you're looking at $10,000+ USD for enough hard drives and NAS systems to store the data. This makes me wonder who on earth has the resources to run these pirate sites. If they wanted to be truly resilient they would also need complete backups multiple times over. You are looking at pretty huge sums of money to mirror sites like Anna's Archive. And who is it who is willing to take such a risk? Probably someone living in a country that is less strict on copyright for one thing. But the immense personal sacrifice of running such an archive and making it publicly available, putting oneself at international risk, again makes me ask: who is doing this? I know _why_ they are doing it. They believe that they are preserving the world's knowledge, disseminating it to those who cannot afford access, and smashing up, in their eyes, unjust copyright systems. Of course, publishers and authors may hold very different views and view them as thieving scum.

In any case. I will continue to watch this space and to see what happens next. Will Anna's Archive disappear soon? What will happen to its enormous collection? And what might spring up like a jack-in-the-box or a whack-a-mole to take its place and to resurrect its complex metadata cataloging system?