---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/01/14/getting-a-custom-sync-service-and-adapter-to-show-up-under-data-and-synchronization-on-android
categories:
- Programming
- Technology
comments: []
date: 2011-01-14 08:14:08 +0100
last_modified_at: 2026-09-06
date_gmt: 2011-01-14 08:14:08 +0100
doi: https://doi.org/10.59348/9jxvd-6t191
roguescholar: https://rogue-scholar.org/records/x9x6c-57t94
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mkw2q4l2u
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Android
- Mendeley
- synchronization
- Java
title: Getting a custom Sync Service and Adapter to show up under "Data and Synchronization"
  on Android
wordpress_id: 564
wordpress_url: http://www.martineve.com/?p=564
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mkw2q4l2u"
kcworks: https://works.hcommons.org/records/8mn20-j9706
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

<p><img src="http://www.martineve.com/wp-content/uploads/2011/01/Android-espaciales-300x225.jpg" alt="Androids!" title="Android-espaciales" width="300" height="225" class="alignnone size-medium wp-image-565" style="margin-top:0px;" /></p>
<p>As mentioned previously, the <a href="http://www.c99.org/2010/01/23/writing-an-android-sync-provider-part-1/">two</a> <a href="http://www.c99.org/2010/01/23/writing-an-android-sync-provider-part-2/">part</a> tutorial on c99.org is a great starting place for people wanting to write their own synchronization service for Android. The only problem is that, because it syncs to Contacts, it omits to tell you what to do to get your new service appearing under Settings -> Accounts -> "Data and Synchronization".</p>
<p>The answer is surprisingly simple, but also elusive. As the tutorial stated, you certainly need:</p>

{% highlight xml %}
      <sync-adapter xmlns:android="http://schemas.android.com/apk/res/android"
          android:contentAuthority="com.martineve.mendroid.data.mendeleycollectionsprovider"
          android:accountType="com.martineve.mendroid.account"
          android:supportsUploading="true"
	  android:userVisible="true"/>
{% endhighlight %}

<p>This on its own, however, is not necessarily enough. It turns out that the check Android performs to ascertain whether to display a sync item underneath the "Data and Synchronization" panel is a call to ContentResolver.getIsSyncable(account), which has to return a positive integer value. This means that, in certain cases (of which I remain unsure), you'll need to call:</p>

{% highlight java %}
ContentResolver.setIsSyncable(account, "com.martineve.mendroid.data.mendeleycollectionsprovider", 1);
{% endhighlight %}

<p>... probably on some form of application startup/install.</p>
<p>If you need further guidance on this, I'd suggest browsing through my work at the <a href="http://code.google.com/p/mendeley-for-android/">Mendeley for Android Google Code repository</a>.</p>