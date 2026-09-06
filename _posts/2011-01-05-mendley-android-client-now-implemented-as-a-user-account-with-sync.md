---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/01/05/mendley-android-client-now-implemented-as-a-user-account-with-sync
categories:
- Programming
- Technology
comments:
- author: 'Tweets that mention Mendley Android Client: now implemented as a user account
    with sync | Martin Paul Eve -- Topsy.com'
  author_email: ''
  author_url: http://topsy.com/www.martineve.com/2011/01/05/mendley-android-client-now-implemented-as-a-user-account-with-sync/?utm_source=pingback&amp;utm_campaign=L2
  content: '[...] This post was mentioned on Twitter by Martin Eve. Martin Eve said:
    New blog post: Mendeley Android Client: now implemented as a user account with
    sync http://martineve.com/?p=527 [...]'
  date: 2011-01-06 06:40:38 +0100
  date_gmt: 2011-01-06 06:40:38 +0100
  id: 6071
- author: David
  author_email: d.hull@sussex.ac.uk
  author_url: ''
  content: Oh gosh, I think Mendeley on Android would make my life complete. Good
    luck!
  date: 2011-01-08 12:17:08 +0100
  date_gmt: 2011-01-08 12:17:08 +0100
  id: 6080
- author: john
  author_email: johnnyb138@gmail.com
  author_url: ''
  content: this client will make my life complete! I have two android devices, a tablet
    and a phone, and would love to help test this out for you! I'm so excited.
  date: 2011-01-25 06:13:27 +0100
  date_gmt: 2011-01-25 06:13:27 +0100
  id: 6147
- author: Joe AVG
  author_email: regular_raju@cooltoad.com
  author_url: ''
  content: Hope you get this thing done soon... I just can't wait for this !
  date: 2011-07-22 09:28:00 +0200
  date_gmt: 2011-07-22 09:28:00 +0200
  id: 6508
date: 2011-01-05 22:51:36 +0100
last_modified_at: 2026-09-06
date_gmt: 2011-01-05 22:51:36 +0100
doi: https://doi.org/10.59348/8tv89-42y78
roguescholar: https://rogue-scholar.org/records/9crdv-6ng61
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mkyfavg2a
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Android
- Mendeley
- Java
title: 'Mendeley Android Client: now implemented as a user account with sync'
wordpress_id: 527
wordpress_url: http://www.martineve.com/?p=527
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mkyfavg2a"
kcworks: https://works.hcommons.org/records/10msc-sgb68
references:
- title: 'Writing an Android Sync Provider: Part 1'
  type: BlogPosting
  url: http://www.c99.org/2010/01/23/writing-an-android-sync-provider-part-1/
  isPartOf:
    name: Did You Win Yet?
    type: Blog
- title: 'Writing an Android Sync Provider: Part 2'
  type: BlogPosting
  url: http://www.c99.org/2010/01/23/writing-an-android-sync-provider-part-2/
  isPartOf:
    name: Did You Win Yet?
    type: Blog
- http://code.google.com/p/mendeley-for-android/ # Mendeley for Android Google Code repository
---

<p>As I made rapid initial progress on the prototype of the Mendeley Client for Android, I started to think about the design. In order to minimize hits on the API, as well as for speedy browsing, it doesn't make sense for the UI to be initiating API calls at every turn. Instead, it would be better, I decided, to implement this via a synchronization service. Unfortunately, this required massive code changes (and I am much indebted to these <a href="http://www.c99.org/2010/01/23/writing-an-android-sync-provider-part-1/">two</a> <a href="http://www.c99.org/2010/01/23/writing-an-android-sync-provider-part-2/">articles</a> for their advice) which have taken me a long time to refactor. While this is a little disappointing (I'd hoped to have the library displaying today), it's a far better structure for sustainable development.</p>
<p>However, this part is done!</p>
<p><object width="480" height="385"><param name="movie" value="http://www.youtube-nocookie.com/v/czEPziT13io?fs=1&amp;hl=en_GB"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube-nocookie.com/v/czEPziT13io?fs=1&amp;hl=en_GB" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="480" height="385"></embed></object></p>
<p>I now have a system that will let you add an account, will check the authentication tokens, refresh them automatically when they expire (well, it will with not much more effort). The next thing to do is to create SQLLite database tables that will hold the synced data and perform the sync once per hour.</p>
<p>If you are interested in how I developed this, the <a href="http://code.google.com/p/mendeley-for-android/">Google Code repository</a> holds the latest efforts.</p>
<p>The exciting news for tomorrow is that I am scheduled in for a phone call with <a href="http://www.mendeley.com/profiles/jason-hoyt/">Jason Hoyt</a>, the Vice-President, R&D and Chief Scientist, of Mendeley, to discuss how the API can better serve the community.</p>