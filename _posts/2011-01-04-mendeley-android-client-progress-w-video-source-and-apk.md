---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/01/04/mendeley-android-client-progress-w-video-source-and-apk
categories:
- Programming
comments:
- author: Tweets that mention Mendeley Android Client Progress (w/ Video, Source and
    APK!) | Martin Paul Eve -- Topsy.com
  author_email: ''
  author_url: http://topsy.com/www.martineve.com/2011/01/04/mendeley-android-client-progress-w-video-source-and-apk/?utm_source=pingback&amp;utm_campaign=L2
  content: '[...] This post was mentioned on Twitter by Martin Eve, Martin Eve. Martin
    Eve said: New blog post: Mendeley Android Client Progress (w/ Video, Source and
    APK!) http://martineve.com/?p=518 #phdchat [...]'
  date: 2011-01-04 19:50:36 +0100
  date_gmt: 2011-01-04 19:50:36 +0100
  id: 6064
- author: Yasin Abbas
  author_email: yasin.abbas@eng.ox.ac.uk
  author_url: ''
  content: "Damn ... and there was a glimmer of excitement there ;]\r\n\r\n\r\nStill,
    glad someone's working on a client!  Good luck with it Martin\r\n\r\n\r\nYaz"
  date: 2011-01-14 06:10:07 +0100
  date_gmt: 2011-01-14 06:10:07 +0100
  id: 6113
- author: Johannes
  author_email: mail@hehejo.de
  author_url: http://hehejo.de
  content: "Hi, I tried to use your app and it's failing at the oauth-step.\r\n\r\nDo
    you have a probably new APK somewhere?\r\n\r\nThanks and keep up with the good
    work,\r\nJohannes"
  date: 2011-01-24 15:21:18 +0100
  date_gmt: 2011-01-24 15:21:18 +0100
  id: 6144
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  content: "Hi, \n\nhoping to have a new release in a day or so."
  date: 2011-01-24 15:44:04 +0100
  date_gmt: 2011-01-24 15:44:04 +0100
  id: 6145
- author: Nick P
  author_email: perry1919@gmail.com
  author_url: ''
  content: "Hey, \n\nHave you made the app? I really want to use mendeley on my phone.
    I'll be getting a Nexus S here in 2-3 weeks and would love to put it on there
    :) \n\nThanks for all your hard work!"
  date: 2011-04-01 00:37:08 +0200
  date_gmt: 2011-04-01 00:37:08 +0200
  id: 6264
date: 2011-01-04 19:19:01 +0100
date_gmt: 2011-01-04 19:19:01 +0100
doi: https://doi.org/10.59348/6a9qn-21p79
roguescholar: https://rogue-scholar.org/records/r19e5-d2m57
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mkyvkew2a
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
title: Mendeley Android Client Progress (w/ Video, Source and APK!)
wordpress_id: 518
wordpress_url: http://www.martineve.com/?p=518
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mkyvkew2a"
kcworks: https://works.hcommons.org/records/jt2kd-y3v51
references:
- http://code.google.com/p/mendeley-for-android/ # Mendeley for Android Google Code project
- http://code.google.com/p/mendeley-for-android/source/checkout # Mendeley for Android source code checkout
- http://code.google.com/p/oauth-signpost/ # OAuth Signpost library on Google Code
- http://www.gnu.org/licenses/ # GNU General Public License page
---

<p>Before anybody non-techie gets excited by the heading there, I'm not claiming this is anywhere near production-ready. In fact, it's not even functional. However, from a technical perspective, my Android Mendeley client has reached a milestone of succesful OAuth login. In this post I will give some samples of the application as it stands, including an APK download, source and video, and also detail the measures I undertook to get OAuth working using Signpost under Java for Android.</p>
<p>First up, there's now a <a href="http://code.google.com/p/mendeley-for-android/">Google Code project</a>, which also includes GPL v3 licensed <a href="http://code.google.com/p/mendeley-for-android/source/checkout">source code</a> of my initial commit.</p>
<p>Secondly, here's a video of the client "in action" (running on the emulator):</p>
<p><object width="480" height="385"><param name="movie" value="http://www.youtube-nocookie.com/v/15DzM6USj74?fs=1&amp;hl=en_GB"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube-nocookie.com/v/15DzM6USj74?fs=1&amp;hl=en_GB" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="480" height="385"></embed></object></p>
<p>Thirdly, if you felt the need to try out this "awesomeness" (read: currently useless fail) on your own device, you can <a href="http://www.martineve.com/MendeleyForAndroid/mendroid.apk">download the apk</a> and install it as an untrusted application.</p>
<p>As you can see, it successfully authenticates, but the API is throwing status 500 Internal Server errors on every API call at the moment. Whether this is a problem at their end, or mine, is unclear for now.</p>
<p><strong>The Seriously Techie Bit</strong></p>
<p>Finally, here's the technical explanation of things I tried, failed and then failed better at:</p>
<p>The first thing to note is that the latest version of <a href="http://code.google.com/p/oauth-signpost/">signpost</a> (1.2.1.1) will NOT work with Mendeley on Android. You'll certainly need 1.2. If you ignore this advice, you requests will all fail at provider.retrieveAccessToken.</p>
<p>Secondly, before calling provider.retrieveAccessToken you need to specify provider.setOAuth10a(true), or you will end up with a response telling you that there was no consumer key provided. Even though there was.</p>
<p>From MendeleyConnector.java:</p>

{% highlight java %}

m_provider.setOAuth10a(true);
m_provider.retrieveAccessToken(m_consumer, code);
{% endhighlight %}

<p>Thirdly, as I mentioned in an earlier post, Mendeley will not allow you to perform a callback to any URL schema except http. For this reason, I have included a php script which must be placed on a webserver and simply performs a URL redirect when the oauth validation token is passed back in:</p>

{% highlight php %}
<?php
/*
 *  
 *  Mendroid: a Mendeley Android client
 *  Copyright 2011 Martin Paul Eve <martin@martineve.com>
 *
 *  This file is part of Mendroid.
 *
 *  Mendroid is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *   
 *  Mendroid is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with Mendroid.  If not, see <http://www.gnu.org/licenses/>.
 *  
 */
if($_GET['oauth_verifier'] != "") {
   header( 'Location: martineve-mendroid:///?oauth_verifier=' . urlencode($_GET['oauth_verifier']) ) ;
}
?>
{% endhighlight %}

<p>Ignore the signpost developers insistence on using the Apache Commons OAuthProvider/Consumer, they don't work whereas DefaultOAuthProvider works fine on signpost 1.2.</p>
<p>If anyone is interested in all the tweaks it took to get the 3 leg phase working, I suggest looking at MendeleyConnector.java (heavily modified from Clemens' version to do a direct callback into the application), but various calls are also in the related activities, MendeleyDroidLogin.java and the onResume function in MainScreenTabWidget (which handles the callback from the browser auth). The portion that is currently failing lies in MendeleyAPITask.java, which will eventually be used properly as an AsyncTask, but is for now just running as a synchronous call from the UI thread to make debugging easier.</p>