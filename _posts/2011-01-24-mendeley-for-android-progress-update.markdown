---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: ! 'Mendeley for Android: Progress update'
wordpress_id: 635
wordpress_url: http://www.martineve.com/?p=635
date: !binary |-
  MjAxMS0wMS0yNCAxOToyNTo1NiArMDEwMA==
date_gmt: !binary |-
  MjAxMS0wMS0yNCAxOToyNTo1NiArMDEwMA==
categories:
- Technology
- Android
- Mendeley
tags:
- Android
- Mendeley
comments:
- id: 6146
  author: ! 'Tweets that mention Mendeley for Android: Progress update | Martin Paul
    Eve -- Topsy.com'
  author_email: ''
  author_url: http://topsy.com/www.martineve.com/2011/01/24/mendeley-for-android-progress-update/?utm_source=pingback&amp;utm_campaign=L2
  date: !binary |-
    MjAxMS0wMS0yNCAyMDowMzoyNSArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMS0yNCAyMDowMzoyNSArMDEwMA==
  content: ! '[...] This post was mentioned on Twitter by mrgunn, Martin Eve. Martin
    Eve said: New blog post: Mendeley for Android: Progress update http://bit.ly/f9XBHx
    [...]'
- id: 6181
  author: ! 'Tweets that mention Mendeley for Android: Progress update | Martin Paul
    Eve -- Topsy.com'
  author_email: ''
  author_url: http://topsy.com/trackback?url=https%3A%2F%2Fwww.martineve.com%2F2011%2F01%2F24%2Fmendeley-for-android-progress-update%2F&amp;utm_source=pingback&amp;utm_campaign=L2
  date: !binary |-
    MjAxMS0wMi0xNyAxODoyMDoxMyArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMi0xNyAxODoyMDoxMyArMDEwMA==
  content: ! '[...] This post was mentioned on Twitter by Sebastian Busse, Carl Boettiger.
    Carl Boettiger said: Exciting things happening with the #Mendeley API http://bit.ly/g0MwVI
    including development for Android http://bit.ly/emFTKy [...]'
- id: 6262
  author: Ettore
  author_email: ettore.landini.el@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0zMCAxNDo1NjoyNCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0zMCAxNDo1NjoyNCArMDIwMA==
  content: Thank you very much for developing this application. There's a way to become
    a beta tester for it? I'm looking forward to trying it out!
- id: 6294
  author: emre
  author_email: emreakbas@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wNS0xMyAxODoyOTo1MyArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNS0xMyAxODoyOTo1MyArMDIwMA==
  content: I'm willing to beta-test it, too.
- id: 6594
  author: Benny Hardjono
  author_email: bennyhardjono@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMi0wMS0xMSAxMTozMTowMCArMDEwMA==
  date_gmt: !binary |-
    MjAxMi0wMS0xMSAxMTozMTowMCArMDEwMA==
  content: Yes include me too bennyhardjono@gmail.com
doi: "https://doi.org/10.59348/ywxj2-82g36"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/01/24/mendeley-for-android-progress-update"
---
<p><img src="http://www.martineve.com/wp-content/uploads/2011/01/WorkingSync-300x224.png" alt="Synchronization with Mendeley" title="WorkingSync" width="300" height="224" class="alignnone size-medium wp-image-636" style="margin-top:0px;" /></p>
<p>This is an update post for my progress on Mendeley for Android.</p>
<p>I have just committed code that provides almost working background synchronization to the device. Indeed, the strange image that you can see here is an emulator dump of the Android logcat while the synchronization procedure is running.</p>
<p>It's probably worth, at this point, detailing a little bit of what I'm doing. After all, there are some other Android clients for Mendeley in the works and they seem to be making rapid progress. My work has been slower, but I believe it is also better designed.</p>
<p>I am implementing the Mendeley API as a background sync service. This means that you perform a sync when you have access to the internet and the content is pulled down to your device for offline browsing. Other implementations appear to be reliant upon a constant internet connection to browse the collection.</p>
<p>Secondly, I am implementing the API under a ContentProvider and as an Account. This means that, in the long run, multiple clients will be able to ask for permission to get hold of the stored Mendeley data; this design does a favour to all working on the platform.</p>
<p>Anyway, there's a couple of bugs left in the sync procedure that I hope to get sorted over the next few days and then I can release a new APK for those who would like to beta test.</p>





