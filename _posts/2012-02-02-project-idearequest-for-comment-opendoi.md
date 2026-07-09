---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2012/02/02/project-idearequest-for-comment-opendoi
categories:
- Technology
- Open Access
- Academia
comments:
- author: Dr Ernesto Priego
  author_email: ''
  author_url: http://twitter.com/ernestopriego
  content: This is excellent Martin, thank you lots for this. Could permalinked academic
    articles (including blog posts and online discussions in academic online hubs)
    get an ODOI? The concept of an Open Object Identifier is exactly what I have been
    pondering about/musing on, but thinking it should be inclusive of online scholarship
    which is de facto excluded from some indexes etc. due to lack of DOI. Could this
    be done?
  date: 2012-02-02 12:23:00 +0100
  date_gmt: 2012-02-02 12:23:00 +0100
  id: 6610
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  content: Certainly. The resolver is simply going to be a unique index key against
    a record, resolve-to address, type and associated metadata foreign key. The scaling
    would become slightly more tricky if any web page was allowed to register, though,
    as it would be theoretically as large as DNS itself...
  date: 2012-02-02 12:27:00 +0100
  date_gmt: 2012-02-02 12:27:00 +0100
  id: 6611
- author: Dr Ernesto Priego
  author_email: ''
  author_url: http://twitter.com/ernestopriego
  content: Sure. Could one apply through a form the way one applies for a ISSN? (Unlike
    ISBNs, ISSNs are still free, at least in the UK). One would not like *everything*
    published online on an academic theme to get one, but if authors/publishers getting
    stuff out without a DOI might want to get an OpenDOI... does this make any sense?
  date: 2012-02-02 12:42:00 +0100
  date_gmt: 2012-02-02 12:42:00 +0100
  id: 6612
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  content: Yep and that sounds sensible to me. Same form as ISSN signup whereby a
    prefix is assigned the first time somebody has some qualifying content. Hence
    the need for volunteers. You'd also want it to be double checked in each instance
    to prevent rogue denials/acceptances.
  date: 2012-02-02 12:49:00 +0100
  date_gmt: 2012-02-02 12:49:00 +0100
  id: 6613
- author: ''
  author_email: chriskeene@gmail.com
  author_url: ''
  content: 'I think one of the biggest mistakes of DOI is not using URIs by default.
    People can refer to them as DOI: 10.1000/182 or http://dx.doi.org/10.1000/182 
    While the latter does tie it to a particular domain, it''s not hard to keep a
    domain name registered. URIs are unique by design and anyone can see that they
    can put them in to a browser and expect to go somewhere useful (which is not immediatly
    obvious from a DOI). '
  date: 2012-02-02 12:51:00 +0100
  date_gmt: 2012-02-02 12:51:00 +0100
  id: 6614
- author: ''
  author_email: chriskeene@gmail.com
  author_url: ''
  content: What API's etc which are currently available from Crossref do you think
    are most useful? The most common Use Case must be resolveing the (Open)DOI to
    a article, which is a sense is performing a similar task to a URL shortener service,
    though we would want more metadata for each item than just a one to one mapping
    (OpenDOI -&gt; publisher URL).
  date: 2012-02-02 12:54:00 +0100
  date_gmt: 2012-02-02 12:54:00 +0100
  id: 6615
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  content: 'Agreed. I always link my DOIs in the human-readable document to the HTTP
    resolver. Following on from our Twitter discussion, the reason for the DOI decision
    is that DOI supports resolving over HTTP or via the Handle protocol. I am not
    in favour of Handle. Tie it to a domain, operate entirely over HTTP. So, amendment
    from this comment would be: ODOIs take the form http://odoi.domain/prefix.identifier'
  date: 2012-02-02 12:55:00 +0100
  date_gmt: 2012-02-02 12:55:00 +0100
  id: 6616
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  content: I think metadata exposure is absolutely key and ensuring that libraries
    have the APIs they'd need to perform automated queries. From there on, you'd probably
    know better than me as to which are useful for libraries! I'm also not sure exactly
    how citation tracking would work and would need to read up on how this is done
    through DOI. Must be some exposed metadata field from each document listing the
    (o)DOIs cited therein. As you've said, the resolver mechanism is so trivial it's
    untrue. .htaccess file redirects all requests to resolver script. Resolver script
    queries primary key of DB and returns url + metadata.
  date: 2012-02-02 12:59:00 +0100
  date_gmt: 2012-02-02 12:59:00 +0100
  id: 6617
- author: Dr Ernesto Priego
  author_email: ''
  author_url: http://twitter.com/ernestopriego
  content: '"Tie it to a domain, operate entirely over HTTP." Yes! The unification
    of protocol is symbolic in this case too. I totally agree with Chris that URIs
    should be default, at least from a humble user perspective!'
  date: 2012-02-02 13:04:00 +0100
  date_gmt: 2012-02-02 13:04:00 +0100
  id: 6618
- author: Geoffrey Bilder
  author_email: gbilder@crossref.org
  author_url: ''
  content: Just FYI, CrossRef actually recommends that CrossRef DOIs be expressed
    as HTTP URIs. See http://goo.gl/peQkn. Also, CrossRef (and DataCite) DOIs support
    content negotiation, which makes them usable for LOD applications. http://goo.gl/P6dFg
    --G
  date: 2012-02-02 18:05:00 +0100
  date_gmt: 2012-02-02 18:05:00 +0100
  id: 6619
- author: Geoffrey Bilder
  author_email: gbilder@crossref.org
  author_url: ''
  content:  I am first to point out that the technology of redirection is not rocket
    science and could be implemented with any number of redirection services including
    the free (as in beer and freedom) Handle or Purl servers. But the real issue is
    the social aspect of managing the URLs. Summary of my take can be found at the
    start of this interview: http://goo.gl/nouE4
  date: 2012-02-02 18:18:00 +0100
  date_gmt: 2012-02-02 18:18:00 +0100
  id: 6620
date: 2012-02-02 12:17:03 +0100
date_gmt: 2012-02-02 12:17:03 +0100
doi: https://doi.org/10.59348/p3n5r-akq92
image:
  feature: geek.png
layout: post
ogImage: geek.png
published: true
status: publish
tags:
- Open Access
- Publishing
- DOI
title: 'Project idea/request for comment: OpenDOI'
wordpress_id: 1881
wordpress_url: https://www.martineve.com/?p=1881
---

<p>Following a conversation (well, a complaint and a suggestion) with <a href="http://www.twitter.com/ernestopriego">@ernestopriego</a> on Twitter, the following came to light (and is certainly something I've experienced):</p>
<p>DOI numbers are assigned by a central organization called CrossRef.<br />
For most quantitive metric computations on academic journal articles, you must assign a DOI.<br />
Membership of CrossRef (for a publisher with less than $1m profit(!)) costs $275/year.<br />
There is a charge per identifier of $1.</p>
<h3>The problem with this setup</h3>
<p>Gold Open Access journals that are run on a purely non-profit basis still have to pay $250/year + $/article. Not much, admittedly, but this money still has to be found. In academia, finding money is difficult.</p>
<h3>The proposal</h3>
<p>Can anybody think of a reason why a parallel, OpenDOI system could not operate?</p>
<p>The technical setup is not huge. Mirroring of CrossRef APIs would be the largest technical task.<br />
The resolver is trivial to write.<br />
The main resource required would be volunteers willing to vet initial publisher applications and coders willing to work with me to write it.</p>
<p>The ODOI number would have to take a different format to DOI numbers. DOI numbers currently look like this: 10.1000/182. An ODOI number could take: ODOI_10.1000/182.</p>
<p>The ODOI resolver could then distinguish between a DOI (whose resolver request could be forwarded to CrossRef) and an ODOI (which it would resolve). This would ensure at least one-way backward compatibility.</p>
<p>The code-base would be open source under a Free license to be decided.</p>
<p>I would favour some form of Python-driven implementation. Perhaps web.py?</p>
<p>I would not advocate, at prototype stage, implementing Handle.</p>
<h3>Sustainability</h3>
<p>It would be feasible to charge for-profit publishers, should they wish to assign an ODOI number but pricing could be lower than CrossRef. This could maintain server costs. I have an initial dedicated server upon which a prototype could be hosted.</p>
<p>Thoughts/comments welcome. I assume the main concern will be fragmentation but would like to hear.</p>
<p><i>Featured image by <a href="http://www.flickr.com/photos/fazen/">fazen</a> under a CC-BY license.</i></p>