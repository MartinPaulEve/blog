---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/06/19/csrf-being-used-in-latest-ipb-vuln-what-about-php-web-request
categories:
- Technology
- InfoSec
- PHP
comments: []
date: 2007-06-19 14:50:21 +0200
date_gmt: 2007-06-19 14:50:21 +0200
doi: https://doi.org/10.59348/jr7ny-stf90
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags: []
title: CSRF being used in latest IPB vuln – what about PHP web request?
wordpress_id: 270
wordpress_url: http://pro.grammatic.org/post-csrf-being-used-in-latest-ipb-vuln--what-about-php-web-request-30.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mndlmmm2i"
---

<p>I was interested to see in a XSS/CSRF exploit the following lines:</p>

{% highlight php %}
if(preg_match("/ipb_admin_session_id=([0-9a-z]{32});/",$data,$stuff))
{
	print '<img width=0 height=0 src="'.$target.'/admin/index.php?adsess='.$stuff[1].'&amp;act=sql&amp;code=runsql&amp;section=admin&amp;query= UPDATE+'.$prefix.'members+SET+mgroup+%3D+%27'.
	$newgroup.'%27+ WHERE+id+%3D+%27'.$member.'%27&amp;st="></img>';
}
{% endhighlight %}

<p>This is obviously designed to be included in a PHP script which should then be included as part of a XSS attack and causes a CSRF attack on IPB to promote a user to administrator status. However, I then got thinking of a far smarter way to perform this type of attack:</p>
<ol>
<li>User visits site including XSS vuln</li>
<li>XSS vuln loads malicious site in an iframe with Cookie Data</li>
<li>PHP/.NET page receives malicious input and issues its own socket request to take actions on the site</li>
</ol>
<p>This approach is far better than just logging cookies because, obviously, cookies can expire. In this methodology the user can be impersonated at the instant they suffer the XSS vulnerability. Furthermore, the power of sockets/WebRequests means that the User Agent could be impersonated. Obviously this approach does not maintain the IP address of the victim, but then again, that is a flawed methodology for securing CSRF vulns. My personal feeling is that for sophisticated attacks this is a far more subtle approach.</p>