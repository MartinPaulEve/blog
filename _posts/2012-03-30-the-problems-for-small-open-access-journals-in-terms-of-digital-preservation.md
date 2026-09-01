---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2012/03/30/the-problems-for-small-open-access-journals-in-terms-of-digital-preservation
categories:
- Digital Preservation
- Open Access
comments:
- author: Adam Rusbridge
  author_email: a.rusbridge@ed.ac.uk
  author_url: http://www.lockssalliance.ac.uk
  content: "Hi Martin,\r\n\r\nIt's great to see discussion of the LOCKSS approach
    for OA content!\r\n\r\nI'd like to note that LOCKSS isn't a dark archive in the
    same way as some of the other journal preservation services are.  A library's
    LOCKSS box integrates into library infrastructure (either the institutional proxy
    or the library link resolver), allowing a library to provide access to content
    when necessary.  One application of this functionality is to provide perpetual
    access to subscription content.\r\n\r\nYou're right to note that LOCKSS content
    is only available to those institutions who have preserved it.  However, we're
    looking at ways to extend this where we know publication is ceasing.  Our ability
    to make the content available more widely is limited by licensing restrictions,
    and so when we know a title is going to cease, in several cases we have negotiated
    release of the content under a Creative Commons open access license.  In one case,
    we've been able to bring out a ceasing titles from behind a paywall and into the
    CC public domain.  \r\n\r\nThis has relevance for ceased content, as it means
    a community member could take on the role of publisher, or it could allow content
    to move from one archiving system to another (e.g. it helps us plan for the event
    of failure in an archiving approach).\r\n\r\nKind regards\r\nAdam"
  date: 2012-04-02 15:47:08 +0200
  date_gmt: 2012-04-02 15:47:08 +0200
  id: 6663
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  content: 'Hi Adam, Thanks for the comment! I entirely appreciate the problems that
    licensing brings; if only all content could somehow be pre-licensed under CC-BY,
    eh? ;) I suppose what I was pining for was some mechanism for light archiving
    work where the permissions are not problematic. I''m still actively thinking about
    all this, and will continue to do so, but I''m not sure the needs of OA journals
    are fully met by the current setup. Also: yes, apologies for not clarifying the
    LOCKSS "dark" archive. It is "dark" in one sense -- I suspect the library would
    prefer to serve content from publishers and keep the archive dark until a trigger
    event happens -- but as your recent SFX demonstration showed, this doesn''t have
    to be the case. Best, Martin'
  date: 2012-04-02 15:58:21 +0200
  date_gmt: 2012-04-02 15:58:21 +0200
  id: 6664
- author: Kevin Hawkins
  author_email: kevin.s.hawkins@ultraslavonic.info
  author_url: http://www.ultraslavonic.info/
  content: An editorial board might choose to partner with a library or other institution
    that pledges to maintain the content even if the journal ceases, as does MPublishing
    ( http://publishing.umich.edu/ ).  Some such institutions even use OJS, and I
    imagine they have a plan in case the sysadmin dies!
  date: 2012-04-03 20:07:47 +0200
  date_gmt: 2012-04-03 20:07:47 +0200
  id: 6675
date: 2012-03-30 16:24:01 +0200
date_gmt: 2012-03-30 16:24:01 +0200
doi: https://doi.org/10.59348/e2826-74m90
image:
  feature: oa.png
layout: post
ogImage: images/oa.png
published: true
status: publish
tags:
- Technology
- OA
- Digital Preservation
title: The problems for small Open Access journals in terms of digital preservation
wordpress_id: 1995
wordpress_url: https://www.martineve.com/2012/03/30/the-problems-for-small-open-access-journals-in-terms-of-digital-preservation/
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7miox62s2n"
---

<p>So, it looks, with the easy reach of software such as <a href="http://pkp.sfu.ca/?q=ojs">Open Journal Systems</a> and <a href="http://annotum.org/">Annotum</a>, as though anybody can create a journal. This is, to a large extent, true. It comes, however, with a problem. Even assuming that you get the editorial board together, have a great first issue and the journal continues, what happens (to take an extreme case) if the server admin dies (I mean real, physical human death)? What happens to the content? How do we preserve content beyond the span of a human life in a digital environment?</p>
<p><img src="https://www.martineve.com/wp-content/uploads/2012/03/safety.jpg" alt="The word SAFETY stencilled in yellow on worn tarmac beside faded hazard stripes" title="Safety" style="width:750px;" class="alignnone size-full wp-image-1999" /></p>
<p>One of the systems that has been designed to make this possible is called <a href="http://www.lockss.org/">LOCKSS</a> (Lots Of Copies Keeps Stuff Safe), and OJS supports this "out of the box". LOCKSS is an advanced, decentralized preservation system that crawls publisher websites, pulls content into a local LOCKSS box and then polls other boxes in the network, at random, to gain consensus on whether there has been damage to its own local copy. The conditions for membership of the <a href="http://www.lockssalliance.ac.uk/">UK LOCKSS Alliance</a> are: 1.) that the journal has been running for 2 years; 2.) that 6 members of the Alliance vote in its favour for preservation.</p>
<p>Other alternatives include <a href="http://www.clockss.org/clockss/Home">CLOCKSS</a> (Controlled Lots Of Copies Keeps Stuff Safe). This is, as they put it:</p>
<blockquote><p>a not for profit joint venture between the world’s leading scholarly publishers and research libraries whose mission is to build a sustainable, geographically distributed dark archive with which to ensure the long-term survival of Web-based scholarly publications for the benefit of the greater global research community.</p>
<p>CLOCKSS is for the entire world's benefit. Content no longer available from any publisher ("triggered content") is available for free. CLOCKSS uniquely assigns this abandoned and orphaned content with a creative commons license to ensure it remains available, forever.</p></blockquote>
<p>However, unlike LOCKSS, CLOCKSS <a href="http://www.clockss.org/clockss/Contribute_to_CLOCKSS">charges a fee</a> for publishers whose revenue falls below $250,000 (!) The fee, for non-profit OA journals, is $200.</p>
<p>Both of these systems operate on the basis of a "dark archive". By this it is meant that content is not accessible in the archive until a "trigger event" (for instance, the journal goes offline) is detected. At that point, CLOCKSS will re-release the content to the world under a CC license, while LOCKSS will make it available to its own member institutions.</p>
<p>Interestingly, both these models were conceived to archive traditional, paywalled content. As a result of OA, therefore, it actually becomes harder to participate in LOCKSS. As the content is provided "free", participating libraries will be, I suspect, less likely to vote for inclusion of OA content; they're more interested in preserving content for which they paid $$s.</p>
<p>I'm pretty sure that I'm going to opt for CLOCKSS for <a href="http://www.excursions-journal.org.uk/">Excursions</a> and <a href="https://www.pynchon.net/index.php/owap">Orbit</a> and have applied to be voted for LOCKSS inclusion on Excursions (Orbit will get its vote when it reaches the age requirement). This does mean, though, that I need to get the funding, year in, year out, for preservation of this content. I am not keen on any form of author-pays scheme to subsidise; if anything, authors should be paid <b>for</b> their work! On the other hand, what do we, as small scholarly OA journals do, in terms of digital preservation?</p>