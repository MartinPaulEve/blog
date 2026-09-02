---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/01/24/mendeley-for-android-progress-update
categories:
- Programming
comments:
- author: 'Tweets that mention Mendeley for Android: Progress update | Martin Paul
    Eve -- Topsy.com'
  author_email: ''
  author_url: http://topsy.com/www.martineve.com/2011/01/24/mendeley-for-android-progress-update/?utm_source=pingback&amp;utm_campaign=L2
  content: '[...] This post was mentioned on Twitter by mrgunn, Martin Eve. Martin
    Eve said: New blog post: Mendeley for Android: Progress update http://bit.ly/f9XBHx
    [...]'
  date: 2011-01-24 20:03:25 +0100
  date_gmt: 2011-01-24 20:03:25 +0100
  id: 6146
- author: 'Tweets that mention Mendeley for Android: Progress update | Martin Paul
    Eve -- Topsy.com'
  author_email: ''
  author_url: http://topsy.com/trackback?url=https%3A%2F%2Fwww.martineve.com%2F2011%2F01%2F24%2Fmendeley-for-android-progress-update%2F&amp;utm_source=pingback&amp;utm_campaign=L2
  content: '[...] This post was mentioned on Twitter by Sebastian Busse, Carl Boettiger.
    Carl Boettiger said: Exciting things happening with the #Mendeley API http://bit.ly/g0MwVI
    including development for Android http://bit.ly/emFTKy [...]'
  date: 2011-02-17 18:20:13 +0100
  date_gmt: 2011-02-17 18:20:13 +0100
  id: 6181
- author: Ettore
  author_email: ettore.landini.el@gmail.com
  author_url: ''
  content: Thank you very much for developing this application. There's a way to become
    a beta tester for it? I'm looking forward to trying it out!
  date: 2011-03-30 14:56:24 +0200
  date_gmt: 2011-03-30 14:56:24 +0200
  id: 6262
- author: emre
  author_email: emreakbas@gmail.com
  author_url: ''
  content: I'm willing to beta-test it, too.
  date: 2011-05-13 18:29:53 +0200
  date_gmt: 2011-05-13 18:29:53 +0200
  id: 6294
- author: Benny Hardjono
  author_email: bennyhardjono@gmail.com
  author_url: ''
  content: Yes include me too bennyhardjono@gmail.com
  date: 2012-01-11 11:31:00 +0100
  date_gmt: 2012-01-11 11:31:00 +0100
  id: 6594
date: 2011-01-24 19:25:56 +0100
date_gmt: 2011-01-24 19:25:56 +0100
doi: https://doi.org/10.59348/ywxj2-82g36
roguescholar: https://rogue-scholar.org/records/e3ben-cta39
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mktl2d62a
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Android
- Mendeley
title: 'Mendeley for Android: Progress update'
wordpress_id: 635
wordpress_url: http://www.martineve.com/?p=635
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mktl2d62a"
kcworks: https://works.hcommons.org/records/sszbn-ds593
---

<p><img src="http://www.martineve.com/wp-content/uploads/2011/01/WorkingSync-300x224.png" alt="Synchronization with Mendeley" title="WorkingSync" width="300" height="224" class="alignnone size-medium wp-image-636" style="margin-top:0px;" /></p>
<p>This is an update post for my progress on Mendeley for Android.</p>
<p>I have just committed code that provides almost working background synchronization to the device. Indeed, the strange image that you can see here is an emulator dump of the Android logcat while the synchronization procedure is running.</p>
<p>It's probably worth, at this point, detailing a little bit of what I'm doing. After all, there are some other Android clients for Mendeley in the works and they seem to be making rapid progress. My work has been slower, but I believe it is also better designed.</p>
<p>I am implementing the Mendeley API as a background sync service. This means that you perform a sync when you have access to the internet and the content is pulled down to your device for offline browsing. Other implementations appear to be reliant upon a constant internet connection to browse the collection.</p>
<p>Secondly, I am implementing the API under a ContentProvider and as an Account. This means that, in the long run, multiple clients will be able to ask for permission to get hold of the stored Mendeley data; this design does a favour to all working on the platform.</p>
<p>Anyway, there's a couple of bugs left in the sync procedure that I hope to get sorted over the next few days and then I can release a new APK for those who would like to beta test.</p>