---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/05/24/csrf-one-time-token-bypass-using-ajax-and-xss
categories:
- Information Security
comments: []
date: 2007-05-24 12:41:15 +0200
date_gmt: 2007-05-24 12:41:15 +0200
doi: https://doi.org/10.59348/xk536-c7k02
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- information security
- XSS
- CSRF
title: (C)SRF one-time token bypass using AJAX and XSS
wordpress_id: 276
wordpress_url: http://pro.grammatic.org/post-csrf-onetime-token-bypass-using-ajax-and-xss-23.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mnhgt7e2e"
---

<p>This morning I knocked up some proof of concept code to illustrate the retrieval of one-time authentication tokens. The situation in which this is handy is when a site follows best practices and implements a one-time authentication token, but is vulnerable to a XSS attack. A one-time authentication token is a hidden value implanted into either a link or form. For example, Digg's one-time token looks like this:</p>

{% highlight html %}
<a href="javascript:dig(0,2075898,'3ba1562c0c94a28b862f8c58fa3b44d3')">digg it</a>
{% endhighlight %}

<p>So, performing the actions in the "dig" function without the correct token (which is issued on a per-session basis) has no effect and will probably trigger a security alert. However, imagine if Digg was found to be vulnerable to a XSS hole - it would be possible to read the token by submitting an AJAX request and then parsing the response. Here is a snippet from the code that does just that:</p>

{% highlight html %}
var match = regexMatch('javascript:dig\(\d,\d+,([^]+)',response);
{% endhighlight %}

<p>This example is not particularly sophisticated, but it illustrates that XSS attacks are NOT protected against by implementing one time-tokens and that CSRF attacks are still entirely possible if a XSS hole is found in the site, tokens or not.</p>