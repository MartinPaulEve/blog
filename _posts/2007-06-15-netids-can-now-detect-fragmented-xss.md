---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/06/15/netids-can-now-detect-fragmented-xss
categories:
- Information Security
- Programming
comments: []
date: 2007-06-15 14:04:15 +0200
date_gmt: 2007-06-15 14:04:15 +0200
doi: https://doi.org/10.59348/p5r60-2gk97
roguescholar: https://rogue-scholar.org/records/ynnhp-zzg22
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mnfei532a
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
- .NETIDS
title: .NETIDS can now detect fragmented XSS
wordpress_id: 272
wordpress_url: http://pro.grammatic.org/post-netids-can-now-detect-fragmented-xss-27.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mnfei532a"
kcworks: https://works.hcommons.org/records/d6dey-r1q42
references:
- http://code.google.com/p/dotnetids # .NETIDS Google Code project page
---

<p>Today I made some large commits to the <a href="http://code.google.com/p/dotnetids">.NETIDS project</a> to enable detection of fragmented XSS attacks.</p>
<p>For an example of what a fragmented attacks looks like, have a look at the .NETIDS SmokeTest. The following url illustrates a fragmented XSS attack:</p>

{% highlight html %}
<a href="http://www.the-mice.co.uk/SmokeTest/SmokeTest.aspx?param1=Hello%20&amp;param2=this%20&amp;param3=is%20a%20test!">http://www.the-mice.co.uk/SmokeTest/SmokeTest.aspx?param1=Hello%20&amp;param2=this%20&amp;param3=is%20a%20test</a>
{% endhighlight %}

<p>As you can see, the resulting markup on the page contains a concaternation of param1, param2 and param3:</p>

{% highlight html %}
fragmented input: Hello this is a test!
{% endhighlight %}

<p>The essence of a fragmented XSS attack is to use this to construct a string from the various concacternations that performs a malicious action. For example, I might try to inject "&lt;" as parameter 1,  "script" as parameter 2 and "&gt;" as parameter 3. This is traditionally very hard to detect because you'd have to permutate through every combination of the strings to see if they form an attack. However, the .NET Framework provides a mechanism for intercepting the rendering of the page and this is the approach taken by .NETIDS.</p>
<p>Step 1: Create an OutputFilter and attach it to Response.Filter:</p>

{% highlight csharp %}
	_oF = new OutputFilter(Response.Filter, this, System.Text.Encoding.ASCII, Server.MapPath("~/IDS/output_filter.xml"));
	_oF.OnPageReady += new OutputFilter.PageReadyEvent(_oF_OnPageReady);
	Response.Filter = _oF;

{% endhighlight %}

<p>Step 2: Write code to take action inside the specified delegate (_oF_OnPageReady)</p>

{% highlight csharp %}
void _oF_OnPageReady(OutputFilter oF)
{
	//Here you can access oF.Report for an IDS report and then either call:
	oF.WriteResponse();

	//which will write out the original page output
	//or
	oF.WriteResponse(string);
	//which allows you to specify an entirely new page output
}

{% endhighlight %}

<p>Pretty nifty huh?</p>
<p>The output filtering has to operate on a smaller set of rules as it must allow most HTML elements but still offers a safeguard against fragmented XSS attacks.</p>
<p>Last but not least, here's a live illustration of page output being caught:</p>
<p><a href="http://www.the-mice.co.uk/SmokeTest/SmokeTest.aspx?param1=%3C&amp;param2=script&amp;param3=%3E">http://www.the-mice.co.uk/SmokeTest/SmokeTest.aspx?param1=%3C&amp;param2=script&amp;param3=%3E</a></p>
<p><b>NOTE WELL: THE .NETIDS PROJECT IS CURRENTLY ON TEMPORARY HOLD AND FRAGMENTED OUTPUT FILTERING IS DISABLED ON THE SANDBOX TEST</b></p>