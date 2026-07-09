---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/11/17/ie7-javascript-modify-the-dom-without-crashing-the-browser
categories:
- Technology
comments: []
date: 2007-11-17 14:53:06 +0100
date_gmt: 2007-11-17 14:53:06 +0100
doi: https://doi.org/10.59348/g9va4-vx923
image:
  feature: geek.png
layout: post
ogImage: geek.png
published: true
status: publish
tags:
- IE7
- DOM
title: IE7 Javascript - modify the DOM without crashing the browser
wordpress_id: 260
wordpress_url: http://pro.grammatic.org/post-ie7-javascript--modify-the-dom-without-crashing-the-browser-40.aspx
---

<p>One of the biggest problems faced when writing Javascript that modifies the DOM is the fact that the poorly written IE7 crashes because it hasn't finished loading the current element. This only seems to happen when the DOM is modified through a script loaded by an xx:expression binding in a style tag.</p>
<p>The only solution that I managed to find was to set an asynchronous timeout:</p>

{% highlight javascript %}
setTimeout('function()',500);
{% endhighlight %}

<p>and then check if the DOM is loaded inside the function:</p>

{% highlight javascript %}
var ne = document.body.innerHTML;

if (ne.indexOf('LAST TEXT BEFORE BODY CLOSE TAG') == -1) {
	setTimeout('function()',500);
	return;
}
{% endhighlight %}

<p>Obviously a far from ideal solution!</p>