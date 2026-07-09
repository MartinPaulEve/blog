---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2008/04/06/binding-to-radiobuttons-in-net-windows-forms
categories:
- Technology
- .NET
comments: []
date: 2008-04-06 09:38:56 +0200
date_gmt: 2008-04-06 09:38:56 +0200
doi: https://doi.org/10.59348/e3wqh-p1b55
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- .NET
- C#
- Windows Forms
title: Binding to RadioButtons in .NET Windows Forms
wordpress_id: 254
wordpress_url: http://pro.grammatic.org/post-binding-to-radiobuttons-in-net-windows-forms-47.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmw3csh2i"
---

<p>Well, it's not security related, but I thought it was worth sharing my solution for all those people who are having trouble binding either ApplicationSettings or any other datasource to a RadioButton in the .NET Framework (C# and VB.NET) WinForms environment.</p>
<p>The problem is that when binding a RadioButton's Checked property clicking on a differentbutton in the set will not select the new option, but merely deselect all options. The reason for this is that the deselect event changes the datasource, the select event never fires and then the whole set are deselected.</p>
<p>The solution is to set the DataSource Update Mode to "Never" (in Visual Studio 2005 go to the Properties window of the RadioButton -&gt; DataBindings -&gt; Advanced and then toggle the value for the selected field.)</p>
<p>Now, this doesn't end the trouble though, because now you have to manually update your datasource in an OK button or similar. This is a problem, especially if it's an ApplicationSettings object because doing the following:</p>

{% highlight csharp %}
Properties.Settings.Default.ASetting = RadioButton.Checked;
{% endhighlight %}

<p>Will alter the settings collection and all the RadioButtons will attempt to rebind, thoroughly messing up your efforts.</p>
<p>Therefore, the way to do it is as follows:</p>

{% highlight csharp %}
bool aBoolean = RadioButton.Checked;

Properties.Settings.Default.ASetting = aBoolean;
{% endhighlight %}

<p>Which is, obviously, incredibly tedious but does at least work. Good luck and here's hoping it gets fixed in .NET 3.5.</p>