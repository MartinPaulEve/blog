---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: JavaScript internal numerical representations
wordpress_id: 265
wordpress_url: http://pro.grammatic.org/post-javascript-internal-numerical-representations-35.aspx
date: !binary |-
  MjAwNy0wNy0wNSAwOTo1OTowMiArMDIwMA==
date_gmt: !binary |-
  MjAwNy0wNy0wNSAwOTo1OTowMiArMDIwMA==
categories:
- Technology
- InfoSec
tags:
- .NET
- Javascript
comments: []
doi: "https://doi.org/10.59348/wacw7-gb986"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/07/05/javascript-internal-numerical-representations"
---
<p>Whilst working on the next release of .NETIDS I came across some interesting info about the parsing of numbers within JavaScript - information that is of particular relevance when it comes to filtering against String.fromCharCode injection attempts. The first item of interest is that JavaScript will parse hexadecimal in the form 0xYY even when not enclosed in quotes (ie. as a string), so this can be used in fromCharCode.</p>
<p>The second interesting issue concerns the following 2 statements:</p>

{% highlight javascript %}
alert(String.fromCharCode(101));

alert(String.fromCharCode(0101));
{% endhighlight %}

<p>When I was writing the parser my maths engine originally assumed that 0101 was equivalent to 101, but in JavaScript this is NOT the case. In JS, a preceding 0 indicates that the number is octal - hence the difference in outcome between the 2 statements.</p>
<p>The table at <a href="http://www.jibbering.com/faq/faq_notes/type_convert.html">http://www.jibbering.com/faq/faq_notes/type_convert.html</a> sums up JS' internal handling of number formats.</p>





