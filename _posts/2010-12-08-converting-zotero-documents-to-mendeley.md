---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/12/08/converting-zotero-documents-to-mendeley
categories:
- Technology
- Academia
comments:
- author: Tweets that mention Converting Zotero Documents to Mendeley | Martin Paul
    Eve -- Topsy.com
  author_email: ''
  author_url: http://topsy.com/www.martineve.com/2010/12/08/converting-zotero-documents-to-mendeley/?utm_source=pingback&amp;utm_campaign=L2
  content: '[...] This post was mentioned on Twitter by Doctoral School, Martin Eve.
    Martin Eve said: New blog post: Converting Zotero Documents to Mendeley http://martineve.com/?p=462
    #phdchat #phd [...]'
  date: 2010-12-08 11:41:46 +0100
  date_gmt: 2010-12-08 11:41:46 +0100
  id: 4013
- author: adam.smith
  author_email: karcher@u.northwestern.edu
  author_url: ''
  content: "From what I can see you're not quite right about Mendeley winning the
    hearts and minds - I think it's a geography thing. Zotero is hugely, hugely more
    popular in the US. It's not even close. And I assume you're right that Mendeley
    is increasingly more popular in the UK - which would just mean that it's easier
    to reach out to the scientific community of the country you're in. \r\n\r\nZotero
    and Mendeley will be one step closer to interoperability once they both use the
    citerproc.js citation generator for csl 1.0. But that still leaves a lot of issues,
    including how to match identifiers and, apparently, how to address the additional
    information Zotero allows you to add to citations - which is indeed critical.
    I think the former is actually much harder to do, the latter, if that's really
    the case, just seems to be a limitation of Mendeley that they need to fix to make
    the software useful for anyone in the social sciences and humanities."
  date: 2010-12-08 14:20:03 +0100
  date_gmt: 2010-12-08 14:20:03 +0100
  id: 4029
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  content: "Hi Adam,\r\n\r\nThanks for that - as you say, I'm working from a UK perspective
    and, from what I hear, Mendeley gets huge uptake relative to Zotero although I
    personally use the latter.\r\n\r\nThe identifier matching shouldn't really be
    a problem. If both plugins exposed the correct APIs, then all that is needed is
    for Mendeley, on import, to store the Zotero identifier in an internal field of
    its own for that specific user prior to document conversion.\r\n\r\nI hadn't heard
    about the citerproc.js plan, but is there, technically, any reason why both sets
    couldn't use the same document plugin system? Admittedly, this would probably
    have to end up being LGPL licensed so as to fit with Mendeley's proprietary nature,
    but would be a huge step forward in terms of interoperability. At the moment,
    reference systems seem to compete on unequal grounds. Once you've got far enough
    into a piece to know whether you like a system, you are unlikely to want to convert
    to another. If this lock-in was eliminated, they could compete on grounds of features
    and user interface.\r\n\r\n(P.S. I'm really pleased about US uptake of Zotero
    -- I'm a big fan, although, as I say, I'd still like to know of and see how Mendeley
    progresses)"
  date: 2010-12-08 17:08:39 +0100
  date_gmt: 2010-12-08 17:08:39 +0100
  id: 4055
- author: adam.smith
  author_email: karcher@u.northwestern.edu
  author_url: ''
  content: "I think the problem with the plugin would be that it also has to work
    with the internal data model of the respective software - things like Zotero groups
    (and whatever Mendeley has in that respect) would probably be an additional challenge.\r\n\r\nI
    think a (very) longterm plan for Zotero is to include citation data in citations
    - that would make conversion easier, I guess.\r\n\r\nAs for the license of a joint
    plugin - I think there would be a reluctance among a good part of Zotero's non-staff
    contributors against LGPL. But I don't see why Mendeley couldn't use a general
    GPL component - actually I think it already does: csl is (I'm pretty sure) released
    under GPL, and almost all csl styles under cc by-sa\r\n\r\nI wonder, though -
    who would have the incentive to put in the significant work? I don't know much
    about Mendeley internals, but Zotero doesn't have a lot of manpower for development
    and I don't them making this a priority.\r\n\r\n(just to clarify my status - I'm
    just an active Zotero user and volunteer some time on the forum - I don't have
    any formal association with or inside knowledge of Zotero)."
  date: 2010-12-08 18:21:27 +0100
  date_gmt: 2010-12-08 18:21:27 +0100
  id: 4062
- author: Mr. Gunn
  author_email: william.gunn@mendeley.com
  author_url: http://mendeley.com/profiles/william-gunn/
  content: Well, at the risk of being unhelpful again, let me point out that Mendeley
    and Zotero do both use citeproc.js, so that's not an issue, it's just that how
    the particular word processor plugins were implemented are different and use different
    field codes.  It would be great if we could agree on a uniform way to do markup
    in word processors, so that Zotero and Mendeley could be used interchangeably
    to format citations in a document, but we just aren't there yet.  I'll bring this
    up for discussion.
  date: 2010-12-09 16:14:14 +0100
  date_gmt: 2010-12-09 16:14:14 +0100
  id: 4228
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  content: "Thanks for that response, Mr. Gunn. I didn't find your response unhelpful,
    it was utterly courteous throughout and only \"unhelpful\" in the sense that,
    for my purposes, it was impractical -- I think Mendeley's approach towards the
    community, especially on Twitter, is exemplary.\r\n\r\nThis is another example
    of that. Nobody from Zotero (I appreciate that they are a community, albeit funded,
    effort, as opposed to a private entity) has initiated that discussion; it is Mendeley
    who are taking the lead.\r\n\r\nThat said, I would be extremely happy if all parties
    were to work together for a standardized citation field reference. At present,
    I am locked-in to Zotero. If this were interchangeable, the reference systems
    would be competing based on their actual merits, rather than a captive user-base,
    which I think we all agree would be a good thing!"
  date: 2010-12-09 16:20:42 +0100
  date_gmt: 2010-12-09 16:20:42 +0100
  id: 4229
- author: adam.smith
  author_email: karcher@u.northwestern.edu
  author_url: ''
  content: "\"Nobody from Zotero (I appreciate that they are a community, albeit funded,
    effort, as opposed to a private entity) has initiated that discussion; it is Mendeley
    who are taking the lead.\"\r\nwell - document conversion has been discussed by
    Zotero and on the Zotero forums for quite a while - and (rightly imho) not limited
    to Mendeley, but more focused on older software like Endnote, which presumably
    has many more locked-in users.\r\n\r\nZotero is also apparently hiring a new community
    liasion/evangelist, which should professionalize that part - I don't know where
    they are on this, the announcement and call for applications was about 2 months
    ago and they sounded very pleased by the applicant pool."
  date: 2010-12-09 17:07:30 +0100
  date_gmt: 2010-12-09 17:07:30 +0100
  id: 4237
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  content: I feel I've been hugely overcritical of Zotero now -- well, perhaps the
    community engagement aspect will change in time....
  date: 2010-12-09 19:32:29 +0100
  date_gmt: 2010-12-09 19:32:29 +0100
  id: 4251
- author: Bruce
  author_email: bdarcus@gmail.com
  author_url: ''
  content: 'I, the creator of the CSL language on which citation support in Mendeley
    and Zotero is based, have long been <a href="http://community.muohio.edu/blogs/darcusb/archives/2009/03/01/the-babel-of-citations"
    rel="nofollow">talking about this</a>.  There is no technical reason at all that
    we couldn''t have a single plug-in code-base and API that could interact with
    different services: mendeley, zotero, citeulike, etc. But someone needs to write
    it.'
  date: 2010-12-29 16:26:28 +0100
  date_gmt: 2010-12-29 16:26:28 +0100
  id: 6029
- author: Bruce
  author_email: bdarcus@gmail.com
  author_url: ''
  content: "Oh, and to offer some balance to this discussion, Zotero was the first
    major CSL implementation, and Mendeley benefited from that groundwork substantially.
    For example. the first Mendeley plugin code was pretty much the same open source
    code Zotero wrote. It just happens that they inherited some of what I consider
    to be the same design mistakes as Zotero ;-).\r\n\r\nSo I'd prefer if  the respective
    user communities would refrain from the competitive language."
  date: 2010-12-29 16:30:41 +0100
  date_gmt: 2010-12-29 16:30:41 +0100
  id: 6030
date: 2010-12-08 08:29:20 +0100
date_gmt: 2010-12-08 08:29:20 +0100
doi: https://doi.org/10.59348/m0c3j-atd18
roguescholar: https://rogue-scholar.org/records/dxfky-8y765
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mljgrqm2i
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- zotero
- Mendeley
- OpenOffice
- Word
- Reference Management
title: Converting Zotero Documents to Mendeley
wordpress_id: 462
wordpress_url: http://www.martineve.com/?p=462
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mljgrqm2i"
kcworks: https://works.hcommons.org/records/2fz6g-yrc84
references:
- http://www.zotero.org # Zotero reference management homepage
- http://www.mendeley.com # Mendeley reference management homepage
- http://feedback.mendeley.com/forums/4941-mendeley-feedback/suggestions/94437-include-page-numbers-in-the-citation # Mendeley feedback request for page numbers in citations
---

<p>One of the best things about Mendeley is that, the second you mention their name on Twitter, a horde of helpful and informative community liaison team members descend upon you. This means that, if you have a query, you can be sure that someone knowledgeable is never far away.</p>
<p>That said, it seems that my current issue -- being able to convert either an OpenOffice or Word <a href="http://www.zotero.org">Zotero</a> document to <a href="http://www.mendeley.com">Mendeley</a> -- is not possible. Having communicated with <a href="http://twitter.com/#!/mrgunn">@mrgunn</a> he suggested two approaches:</p>
<ol>
<li>Save the document without Zotero markup and re-insert the citations</li>
<li>Run the document through a LaTeX converter (untested)</li>
</ol>
<p>As the document in question has over 500 citations, I didn't find this to be of much use (which is not a criticism of <a href="http://twitter.com/#!/mrgunn">@mrgunn</a>, but rather the sad state of interoperability). However, I decided to do a little digging myself to work out what the actual issues are...</p>
<p>Now, in OpenOffice (at least), a Zotero field code looks like this: Reference: ZOTERO_ITEM {"citationItems":[{"locator":"17","uri":["http://zotero.org/users/64077/items/WKMCH3XK"]}]} RND5qVC9BQOk1. Upon visiting the URL in question, it is quite clearly a Zotero catalogue entry. A Mendeley citation, on the other hand, looks like: Reference: Mendeley Citation{f19dafe4-bd54-4b6c-9585-7acfd39428c9} RNDSDLGneoN3n. The task of a converter would be to match these two styles up. </p>
<p>However, it doesn't seem to be that simple. Zotero reference fields can also contain a plethora of other information that Mendeley seemingly doesn't support, the foremost (and to my mind a deal-breaker) being <a href="http://feedback.mendeley.com/forums/4941-mendeley-feedback/suggestions/94437-include-page-numbers-in-the-citation">page numbers</a> (!) This means that any conversion to Mendeley's format would be lossy; it would be impossible to preserve all the data from Zotero citations because Mendeley simply doesn't support including all this information.</p>
<p>While Mendeley seems, from my Twitter conversations, to be winning the hearts and minds of the research community, time and time again I query whether this is because they have a superior product to, say, Zotero or because they are able to market it better owing to the monetarization of their service. Things they win on: pretty interface; social aspect of sharing; online profiles generated automatically are great. Sadly, however, some basic stuff is missing. If they could implement this and then work with Zotero to allow document cross-compatibility (alongside not asking me to enter my email password to garner contacts -- this is incredibly bad practice -- OAuth?), they'd be on to a winner with a superior product.</p>