---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: ! 'OAuth for Mendeley on Android: solved and a bug'
wordpress_id: 515
wordpress_url: http://www.martineve.com/?p=515
date: !binary |-
  MjAxMS0wMS0wNCAwNjozMTo0NCArMDEwMA==
date_gmt: !binary |-
  MjAxMS0wMS0wNCAwNjozMTo0NCArMDEwMA==
categories:
- Technology
- Android
tags:
- Android
- Mendeley
- Java
comments:
- id: 6062
  author: ! 'Tweets that mention OAuth for Mendeley on Android: solved and a bug |
    Martin Paul Eve -- Topsy.com'
  author_email: ''
  author_url: http://topsy.com/www.martineve.com/2011/01/04/oauth-for-mendeley-on-android-solved-and-a-bug/?utm_source=pingback&amp;utm_campaign=L2
  date: !binary |-
    MjAxMS0wMS0wNCAwNzoxNjo0MiArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMS0wNCAwNzoxNjo0MiArMDEwMA==
  content: ! '[...] This post was mentioned on Twitter by Martin Eve, Martin Eve.
    Martin Eve said: New blog post: OAuth for Mendeley on Android: solved and a bug
    http://martineve.com/?p=515 [...]'
doi: "https://doi.org/10.59348/2sbef-mtt65"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/01/04/oauth-for-mendeley-on-android-solved-and-a-bug"
---
<p>Thanks to Clemens' comment on my last post, I have managed to track down the problems that I was having with OAuth for Mendeley on Android; it's all callback related.</p>
<p>It seems that callbacks to any protocol except "http" are prohibited.</p>
<p>For instance:</p>
<p>A callback request to "http://www.martineve.com" will work.<br />
A null callback request ("out of bound"/"OOB") will work and display PIN.<br />
A callback request to "martineve-mendroid:///" will fail.</p>
<p>The failure message varies between "consumer key not found" and a pretty "Something went wrong" page.</p>
<p>I have also tested with addresses that look like URLs from a regex point of view: "eeee://www.test.com". This also fails, so it must be the prefix.</p>
<p>The reason that this feature is required is that Android allows the hooking of URLs to specific Intents, so the web browser can pass the code directly back to the non-web browser application.</p>
<p>In the meantime, I have a workaround for this that should allow me to get on with writing the application. Thanks to Clemens for his original source and here's to hoping the Mendeley devs can come up with a fix, at which point I will make a post detailing how to do this.</p>





