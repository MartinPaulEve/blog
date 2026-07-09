---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2016/12/13/introducing-cemmento-a-digital-preservation-tool-for-annotations
date: 2016-12-13
doi: https://doi.org/10.59348/arjxf-k7e88
image:
  feature: geek.png
layout: post
ogImage: geek.png
title: 'Introducing Cemmento: A digital preservation tool for annotations'
---

Annotation tools on the web are somewhat fragile. They depend upon complex XPath queries and other anchoring technologies to ensure that annotations are keyed to known positions.

The problem is that often, even where content is _stable_ in one sense (e.g. in an academic journal article), redesigns of the page itself can lead to serious problems for annotation keying. This creates orphan annotations.

Alex Gil, Ben Armintor, and I sat down this morning at Columbia and decide to do something about this. We have now created a proxy application, [Cemmento](https://github.com/MartinPaulEve/cemmento/tree/master), that redirects users to a canonical version of a document for shared annotation on the first known stable edition.

URLs to Cemmento take the following form: [https://cemmento.org/https://www.martineve.com/2016/12/09/the-thing-thats-gone-missing-in-the-revisions-to-the-ref-consultation-between-february-and-december-2016/](https://cemmento.org/https://www.martineve.com/2016/12/09/the-thing-thats-gone-missing-in-the-revisions-to-the-ref-consultation-between-february-and-december-2016/)

Cemmento does the following:

1. When a URL is passed, it checks whether a version exists in the storage backend (in this case, the Internet Archive) with the querystring ?cemmento.

2. If a version does not exist, Cemmento requests the internet archive to store a copy.

3. Cemmento redirects the user to the earliest copy on the internet archive, using a Via service to automatically load a commenting/annotation engine (in this case, Hypothesis).

There are several assumptions behind this:

1. We are dealing with material that is stable and that design changes are causing orphan annotations. Scholarly communications generally fall in this category.
2. That we therefore want to redirect users to an archived copy for annotation to maximize collaboration and stability at the same time.

We have tried to write Cemmento so that alternative storage, query, and redirect modules can be substituted in without too much difficulty. A sample proxy version is available at cemmento.org.

The default expected behaviour is that users will be redirected to an internet archive version of the requested URL with the hypothesis annotation sidebar loaded.