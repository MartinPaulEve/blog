---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/06/26/httponly-cookies-in-net-2-0
categories:
- Information Security
- Programming
comments: []
date: 2007-06-26 17:24:31 +0200
date_gmt: 2007-06-26 17:24:31 +0200
doi: https://doi.org/10.59348/75sxs-sqj29
roguescholar: https://rogue-scholar.org/records/92mvw-sfx34
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mnbkop32e
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- .NET
title: HttpOnly cookies in .NET 2.0
wordpress_id: 266
wordpress_url: http://pro.grammatic.org/post-httponly-cookies-in-net-20-34.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mnbkop32e"
---

<p>This is a well known trick that I just wanted to share as it is so crucial in preventing effective XSS attacks in Internet Explorer (and hopefully soon FireFox).</p>
<p>Anyway, the method is simple, whack this under the &lt;system.web&gt; section of your web.config file:</p>

{% highlight xml %}
<httpCookies httpOnlyCookies="true" requireSSL="false" domain="" />
{% endhighlight %}

<p>Tada!</p>