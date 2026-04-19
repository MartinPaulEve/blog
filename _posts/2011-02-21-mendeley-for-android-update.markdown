---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Mendeley for Android Update
wordpress_id: 801
wordpress_url: https://www.martineve.com/?p=801
date: !binary |-
  MjAxMS0wMi0yMSAxMDozMDoxMyArMDEwMA==
date_gmt: !binary |-
  MjAxMS0wMi0yMSAxMDozMDoxMyArMDEwMA==
categories:
- Technology
- Android
- Mendeley
tags:
- Android
- Mendeley
comments:
- id: 6190
  author: CWinkler
  author_email: microwink@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMi0yNCAwMjoxNjoyNSArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMi0yNCAwMjoxNjoyNSArMDEwMA==
  content: I'm very happy to hear that you're making progress!
- id: 6191
  author: gushamilton
  author_email: gushamilton@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0wMSAxODo1Njo1MyArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0wMSAxODo1Njo1MyArMDEwMA==
  content: Thanks for this. Seriously, this will be really useful. Hope it's not too
    much work!
- id: 6212
  author: Mark Lifson
  author_email: mlifson@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0wOSAxNTo1OTowNyArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0wOSAxNTo1OTowNyArMDEwMA==
  content: Will you let us know when it becomes available on the market?
- id: 6213
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0wOSAxNTo1OTo1OCArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0wOSAxNTo1OTo1OCArMDEwMA==
  content: I will do; just so bogged down in work at the moment that this has had
    to take a back seat.
- id: 6263
  author: magdalena avena
  author_email: mavena@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0zMSAxMzoyODozNSArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0zMSAxMzoyODozNSArMDIwMA==
  content: ! "thank you very much... it will be essential for my job. i´ll wait with
    very anxiety (sorry, brazilian english) \n\nmavena"
- id: 6274
  author: cabotine
  author_email: cabotine@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wNC0wNSAxMToxNTo1OSArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNC0wNSAxMToxNTo1OSArMDIwMA==
  content: ! "any news on Mendeley for Android?\r\nbtw the category-rss-feed for android
    is pointing to all of your posts not just the android ones \r\nRegards\r\nC."
- id: 6277
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wNC0xMCAxMDo0OTowMSArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNC0xMCAxMDo0OTowMSArMDIwMA==
  content: Hi all who asked. I am still working on this, but it's much more slowly
    than I would like. I have been hit by about ten billion work things at once!
- id: 6288
  author: Eric Astor
  author_email: eric.astor@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wNS0wNCAxOTowMjo1NSArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNS0wNCAxOTowMjo1NSArMDIwMA==
  content: I know you've posted source before - I'd be happy to lend a hand, and I
    suspect others might be as well. Any chance of setting up an open-source repository
    and accepting contributions? Github, Google Code, SourceForge...
- id: 6289
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wNS0wNCAxOToxNjowMyArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNS0wNCAxOToxNjowMyArMDIwMA==
  content: ! 'Hi Eric,
    All the code is available at http://code.google.com/p/mendeley-for-android/ --
    the only change needed is to put in your API key.
    Any help would be greatly appreciated. I''m completely overrun here.
    Martin'
- id: 6507
  author: Angela
  author_email: demonio.rojo@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wNy0xNyAwNDo1ODowMCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNy0xNyAwNDo1ODowMCArMDIwMA==
  content: ! 'Wow, if I had time I will help you this this, but I don''t not anything
    on how to program this, but just want to cheer you up, look it very nice!!!
    Waiting for it!!    '
doi: "https://doi.org/10.59348/tz8rw-80w60"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/02/21/mendeley-for-android-update"
---
<p>A few weeks ago, I tweeted that the first beta of Android for Mendeley was almost ready. This post is an update on that status. I'm afraid to say that, about ten minutes after I posted that status, I ran a test on the oAuth code only to find that it was not working. This was strange as I had made no changes and it was previously working. I immediately got in touch with the Mendeley API team (particularly the extremely helpful @phpeach) who promised to have a look.</p>
<p>The problem is, they are busy busy people, and I don't blame them for this. It has, therefore, taken a lot longer for the fix to come through.</p>
<p>The good news is that this has now been fixed at Mendeley's end and I can continue development. Here's what's left to do:</p>

* Finalize and create layout for individual item view
* Add automated synchronization option (in pre-Froyo OS, this is more complicated as I can't ask Android to schedule it)

<p>I'm away all this week (scheduled posts FTW), but will attempt to get this on the market in the near future (ie. end of next week).</p>





