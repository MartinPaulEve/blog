---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: HttpOnly cookies in .NET 2.0
wordpress_id: 266
wordpress_url: http://pro.grammatic.org/post-httponly-cookies-in-net-20-34.aspx
date: !binary |-
  MjAwNy0wNi0yNiAxNzoyNDozMSArMDIwMA==
date_gmt: !binary |-
  MjAwNy0wNi0yNiAxNzoyNDozMSArMDIwMA==
categories:
- Technology
- .NET
tags:
- .NET
comments: []
doi: "https://doi.org/10.59348/75sxs-sqj29"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/06/26/httponly-cookies-in-net-2-0"
---
<p>This is a well known trick that I just wanted to share as it is so crucial in preventing effective XSS attacks in Internet Explorer (and hopefully soon FireFox).</p>
<p>Anyway, the method is simple, whack this under the &lt;system.web&gt; section of your web.config file:</p>

{% highlight xml %}
<httpCookies httpOnlyCookies="true" requireSSL="false" domain="" />
{% endhighlight %}

<p>Tada!</p>





