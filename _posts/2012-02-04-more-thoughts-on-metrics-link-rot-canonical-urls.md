---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2012/02/04/more-thoughts-on-metrics-link-rot-canonical-urls
categories:
- Technology
- Open Access
comments:
- author: Dr Ernesto Priego
  author_email: ''
  author_url: http://twitter.com/ernestopriego
  content: '"DOI is about finding a way to ensure preservation of items beyond the
    lifespan of a human being." That''s why, as a user, reader, author and publisher,
    I wish it were easier and more affordable to get DOIs. The fact is that in academia,
    the result of the existing system is that any academic work without a DOI is hierarchically
    inferior, if not inexistent. The solution as you say may not be an alternative
    system, but I still believe this issues deserve to be raised and discussed. I''ve
    been often asked by academics to explain what a DOI is. This is something everyone
    in academia should know about. The fact many don''t is symptomatic of something
    that deserves serious scrutiny. '
  date: 2012-02-04 19:22:00 +0100
  date_gmt: 2012-02-04 19:22:00 +0100
  id: 6622
- author: Euan Adie
  author_email: euan.adie@gmail.com
  author_url: ''
  content: Very true. This doesn't detract from your point but when it comes to articles
    &amp; datasets (figures, datasets, blog posts etc. are slightly different...)
    the financial burden for individuals should be shouldered by your institution,
    really - for example institutional repositories can mint DOIs for free / very
    little cost via organizations like Datacite. For publishers the cost to mint a
    DOI should be relatively low (~ $1), is that not the case?
  date: 2012-02-04 20:54:00 +0100
  date_gmt: 2012-02-04 20:54:00 +0100
  id: 6623
date: 2012-02-04 19:12:27 +0100
date_gmt: 2012-02-04 19:12:27 +0100
doi: https://doi.org/10.59348/g1dhf-05144
layout: post
published: true
status: publish
tags:
- Open Access
- Publishing
- DOI
title: More thoughts on metrics, link-rot, canonical URLs
wordpress_id: 1895
wordpress_url: https://www.martineve.com/2012/02/04/more-thoughts-on-metrics-link-rot-canonical-urls/
---

<p>In my <a href="https://www.martineve.com/2012/02/03/dois-what-you-need-to-know/">previous post</a>, I flagged up a conversation about DOIs that I had with Geoffrey Bilder on Twitter. It was enlightening in many ways; I hadn't appreciated that one of the main challenges faceed by Crossref is a carrot and stick approach to ensure that DOIs really do combat link rot.</p>
<p>A further conversation was ongoing on Twitter today:</p>
<p>http://storify.com/martin_eve/dois-handle-and-federated-identifiers</p>
<p>This raises several good points and it's worth relating them to the way that the current DOI system works. First off, the explicit purpose of a DOI is as follows:</p>
<blockquote><p>They are used to provide current information, including where they (or information about them) can be found on the Internet. Information about a digital object may change over time, including where to find it, but its DOI name will not change.</p></blockquote>
<p>So, the function of a DOI is to hold, in a central location, up-to-date information about a "digital object" and tie various pieces of metadata to that record; most importantly, its absolute current location. The knock-on effect, although not specifically in the remit of that DOI definition, is that citation tracking/scholarly metrics become possible because of a single identification number.</p>
<p>As detailed before, financial penalties are tied to this centralized system because its very function is to ensure, through coercion and incentive, that publishers keep their record current. If the central DOI mechanism becomes internally inconsistent or out of date, it is useless. It is proposed (although never tested) that without financial penalties tied to real-world currency, this system would be unable to fulfill its role.</p>
<p>The second interesting point to note is that DOI is an implementation of the <a href="https://en.wikipedia.org/wiki/Handle_System">Handle System</a>. The key aspect here is that, although as researchers we are most likely to use a DOI resolver over HTTP via doi.org, <a href="http://www.handle.net/rfc/rfc3650.html">Handle is not tied to DNS</a>. It's closer to being a form of distributed darknet:</p>
<blockquote><p>It is probably best to view the Handle System as a name-attribute binding service with a specific protocol for securely creating, updating, maintaining, and accessing a distributed database. (RFC 3650)</p></blockquote>
<p>Ultimately, then, Handle is a very well thought through mechanism for dealing with this problem. Where, though, does it leave those who want DOI numbers without monetary attachment. Answer: up in the air. Your URLs are federated (and could therefore be used as a unique identifier for metrics, even if you don't own the domain; scholarly metrics would be independent of domain ownership), but as they are controlled through DNS/tied to a web server, as Euan pointed out, they frequently go off the radar.</p>
<p>It would be possible, as I had proposed in my <a href="https://www.martineve.com/2012/02/02/project-idearequest-for-comment-opendoi/">initial, somewhat naive statement</a>, to create a basic centralized service over HTTP and DNS that assigned a consistent URL that could be updated and thereby tracked for citations. However, there would be no guarantee of the stability of such a service. If it doesn't protect against link rot, then there will be no evidence that it is solid enough for preservation and metrics. Furthermore, its direct tie to DNS (remember: you don't own a domain) makes it little more guaranteed than the original site. To give a quick example:</p>
<p>Say we setup an identifier system: opendoi.org.<br />
My article at hurrahnewjournal.org/eve/2012/01/shiny_peer_reviewed_article is given an identifier: opendoi.org/shiny12345<br />
Now, a year down the line, hurrahnewjournal runs into difficulty. It moves address, but looks like it will fold in a few years. The journal maintainers don't update their record because there is no penalty. The OpenDOI is also now worthless as a form of preservation.</p>
<p>Even more catastrophic, though, is the question of who guarantees opendoi. If the central service is no more guaranteed to be preserved than the records it points to, then what value does it add? From all my reading on this over the past few days, DOI and Handle are ways to mitigate against this through central authority, a distributed system, evasion/non-centrality of DNS and financial incentives to ensure records are current. I may not believe that money is a true motivator in life, but in this small subset it seems to work to maintain the system's integrity. I would welcome a discussion on how this could be opened up so as to exclude the financial element, though, perhaps with tiered incentives?</p>
<p>DOI is about finding a way to ensure preservation of items beyond the lifespan of a human being. Any alternative system, free of monetary charge or not, must do equally as well in the target areas specified here and, sadly, I think it unlikely that an effort provided over HTTP and DNS would do so.</p>
<p><i>Featued image by <a href="http://www.flickr.com/photos/labanex/">labanex</a> under a CC-BY-NC-SA license.</i></p>