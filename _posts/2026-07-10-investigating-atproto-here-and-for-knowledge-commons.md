---
archive: 'https://wayback.archive-it.org/22123/20241101171236/https://eve.gd/2026/07/10/Investigating-atproto-here-and-for-knowledge-commons'
date: '2026-07-10'
doi: https://doi.org/10.59348/r3x69-k5d70
kcworks: https://works.hcommons.org/records/a4vce-d3a56
image:
  credit: GuerillaBuzz on Unsplash
  creditlink: https://unsplash.com/@guerrillabuzz?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText
  feature: decentral.jpg
  title: An abstract image of a network
layout: post
ogImage: images/decentral.jpg
references:
- author:
    name: Brennan Kenneth Brown
    orcid: https://orcid.org/0009-0004-6725-8425
  date: 2026-06-26
  isPartOf:
    name: "Brennan's Weblog"
    type: Blog
    url: https://brennan.day/
  language: en
  license: https://creativecommons.org/licenses/by-sa/4.0/
  title: Publishing My Eleventy Blog to the ATmosphere with Standard.site
  type: BlogPosting
  url: https://brennan.day/publishing-my-eleventy-blog-to-the-atmosphere-with-standard-site/
title: 'Investigating ATProto here and for Knowledge Commons'
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mqcjjtkq4c2e"
categories:
- Scholarly Communications
---

After a recent post by [Brennan Kenneth Brown](https://brennan.day/publishing-my-eleventy-blog-to-the-atmosphere-with-standard-site/), I decided to investigate what it would take to get this site -- and, then, Knowledge Commons -- onto the ATmosphere, using ATProto. This was a pretty steep learning curve, as I did not, before, understand many of the key concepts in this space. After succeeding, though, in publishing this blog to the ATmosphere (I took Brennan's excellent advice to proceed immediately to Sequoia) I am left pondering.

First, what is this ATmosphere thing? Well, it's the protocol behind Bluesky and, basically, it provides a decentralized storage system for objects of any type. Bluesky posts have a type of "app.bsky.feed.post" while my blog posts are "site.standard.document". Various new platforms are emerging that can read and write to the ATmosphere, so it gives a new discovery layer (see [e.g. this search](https://pckt.blog/read?search=martin+eve+fair+square)), but also, in theory, a decoupled presentation layer; so how the site appears will be in the hands of the receiver, rather than determined by the writer. 

Now, though, let's see what I have achieved... If you visit a recent post, you may notice that there are now two link tags in the document head:

```html
<link rel="site.standard.document" href="at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lupu73d2i">
<link rel="site.standard.publication" href="at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.publication/3mq4tnwmt3w2i">
```

These links tie the page to its ATmosphere equivalent. Now, you can't just browse the ATmosphere in a web browser. The content has to have an interface written in front of it, that pulls the content in from this protocol and displays it. However, no fear, because there's an experimental browser for it! So, if you [visit the corresponding file](https://www.atproto-browser.dev/at/did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lupu73d2i), you can, indeed, confirm that I have been successful in getting my content in.

So, interestingly, there are no current standard.site or standard.document aggregators that display the document in their own interface (at least that I could see). Everywhere I tried linked back to the canonical web reference. But, interestingly, they WERE able to find the content and pull it into their aggregation streams.

Another advantage is that, if my current PDS (where the data is stored -- a Personal Data Server -- which is actually on Bluesky's servers, as they run my current storage location) decides to shut down or move, and I no longer wish to be on their system, I can move the files and everything will apparently just be nicely migrated, without needing permission from the old PDS. Well, that sounds good, but I haven't tried it.

However, the entire reason I did this experiment was to see whether this was something worth pursuing for [Knowledge Commons](https://hcommons.org).

... and, for now, I am not sure. At the scale that we operate over there, it would take some effort to make sure we were doing it right. I also think that we would need to run our own PDS. On my personal blog, I hit the daily rate limit when I tried to upload 994 blog posts and associated file blobs (cover images etc.)... and then tried to modify every single one of them. I was locked out of Bluesky's PDS for 24hrs, which was annoying. However, KC has many, many more blog posts than this that would require initial loading. And if we ever had to do a full forced update of all content (say the canonical URL changed - gasp!), the process would need batching, it would be a pain, etc. But running our own PDS is also a pain. It's a whole new infrastructure that needs tending, opening new security holes, exposing us to the outside world... and that could go wrong.

Hence, my conclusion is that, for now, I think we should watch and wait. If there is really substantial traction in this place -- or if lots of people ask for it -- I will certainly reconsider. But I would feel some trepidation about boldly going into this space, right now.