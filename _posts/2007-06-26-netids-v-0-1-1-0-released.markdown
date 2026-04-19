---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: .NETIDS v.0.1.1.0 released
wordpress_id: 268
wordpress_url: http://pro.grammatic.org/post-netids-v0110-released-32.aspx
date: !binary |-
  MjAwNy0wNi0yNiAxNjoyODoyMSArMDIwMA==
date_gmt: !binary |-
  MjAwNy0wNi0yNiAxNjoyODoyMSArMDIwMA==
categories:
- Technology
- InfoSec
- .NET
tags:
- information security
- .NET
- C#
- .NETIDS
comments: []
doi: "https://doi.org/10.59348/r4g1g-6s974"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/06/26/netids-v-0-1-1-0-released"
---
<p>Just a quick note to announce the release of .NETIDS v.0.1.1.0 - a small update that adds some valuable features:</p>
<ul>
<li>Fixed bug of empty Report.Tags object</li>
<li>Added options to SecurePage to disable each type of scanning</li>
<li>Updated filters</li>
</ul>
<p>Most significantly this means that you can control whether page Output Scanning  is performed from a SecurePage derived page. For those who are unaware, SecurePage is the simplest inbuilt way of scanning a page in .NETIDS. Simply inherit your page from SecurePage:</p>

{% highlight csharp %}
public partial class _Default : DOTNETIDS.SecurePage
{
}
{% endhighlight %}

<p>and add the method</p>

{% highlight csharp %}
public override void IDSEventHandler(DOTNETIDS.Report report, DOTNETIDS.SecurePage SecurePage)
{% endhighlight %}

<p>This will ensure that your page is scanned in a secure-by-default fashion and also gives the option to disable each type of scan and add exclusions.</p>
<p>The latest package is available at the dotnetids homepage: <a href="http://code.google.com/p/dotnetids/">http://code.google.com/p/dotnetids/</a></p>





