---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2024/01/09/rusting-away-or-packing-the-entire-crossref-database-into-a-sqlite-file
date: 2024-01-09
last_modified_at: 2026-09-06
doi: https://doi.org/10.59348/5tkbp-dpa74
roguescholar: https://rogue-scholar.org/records/n2kwv-95q42
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lx65usa2f
image:
  feature: header_rust.png
layout: post
ogImage: images/header_rust.png
title: 'Rusting Away (or: packing the entire Crossref database into a SQLite file)'
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lx65usa2f"
categories:
- Programming
- Scholarly Communications
kcworks: https://works.hcommons.org/records/vzxv9-cap71
references:
- title: rustsqlitepacker
  type: SoftwareSourceCode
  url: https://gitlab.com/crossref/labs/rustsqlitepacker
  isPartOf:
    name: GitLab
    type: WebSite
---

Over the past few weeks I've been working to pack the entire Crossref database into a distributable SQLite file. While this sounds somewhat insane -- the resulting file is 900GB -- it's quite a cool project for, say, embedded systems work in situations where no internet connection is available. It also provides speedy local indexed lookups, working faster than the internet-dependent API ever could.

There were some snags I hit along the way:

1. I had to write [the whole thing in Rust](https://gitlab.com/crossref/labs/rustsqlitepacker). It turns out that you can do it in Python, but I got much better speeds doing it all in Rust.
2. An ORM approach in Python was far too slow.
3. Setting the PRIMARY KEY to be the DOI on the database was a bad idea. There are so many commonalities in prefixes that the B-tree just grew and grew until the whole program was abort(3)-ed for an out of memory error, taking down the terminal emulator in which it was running, too. Rust does _not_ recover well from OOM errors.
4. It's best to build the index of DOIs at the end, once the data is in place.
5. In Rust, you can use a bounded channel to read data and block until it's been processed in a writer thread. This was a neat way of reading the tar.gz files at max speed but not exceeding the memory capacity of the host machine,