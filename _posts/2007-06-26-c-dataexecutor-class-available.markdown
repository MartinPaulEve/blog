---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: C# DataExecutor class available
wordpress_id: 267
wordpress_url: http://pro.grammatic.org/post-c-dataexecutor-class-available-33.aspx
date: !binary |-
  MjAwNy0wNi0yNiAxNjozODoxMSArMDIwMA==
date_gmt: !binary |-
  MjAwNy0wNi0yNiAxNjozODoxMSArMDIwMA==
categories:
- Technology
- .NET
tags:
- .NET
- C#
- MySQL
comments:
- id: 188
  author: C# DataExecutor class again | Martin Paul Eve
  author_email: ''
  author_url: http://www.martineve.com/2008/07/31/c-dataexecutor-class-again/
  date: !binary |-
    MjAxMC0xMS0wNyAxMjozMDowOCArMDEwMA==
  date_gmt: !binary |-
    MjAxMC0xMS0wNyAxMjozMDowOCArMDEwMA==
  content: ! '[...] been asked some further questions about the DataExecutor class
    on FreeNode and thought I&#8217;d give some usage instructions/clarification [...]'
doi: "https://doi.org/10.59348/gepnb-vc464"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/06/26/c-dataexecutor-class-available"
---
<p>One of the questions I see most frequently on Freenode's ##csharp irc channel is how to use a MySql Database in .NET. I've therefore provided the class that I use for basic database operations. You can find it at <a href="http://www.martineve.com/2007/06/25/c-mysql-dataexecutor-class/">http://www.martineve.com/2007/06/25/c-mysql-dataexecutor-class/</a>.</p>
<p>The class supports both strongly and weakly typed datasets and usage is as follows:</p>
<ol>
<li>Get the MySql Connector.NET</li>
<li>Reference it in your project</li>
<li>Use the following for strongly typed datasets:</li>
</ul>

{% highlight csharp %}
MySql.Data.MySqlClient.MySqlCommand cmd = new MySql.Data.MySqlClient.MySqlCommand("SELECT * FROM table WHERE blah=@blah");
cmd.Parameters.Add("@blah", "test");

Tools.DataExecutor de = null;

try{

	de = new Tools.DataExecutor(cmd, false);

	DataSchemas.app.tableDataTable test = new DataSchemas.app.tableDataTable();
	de.DataSetSchema(test);

	DataSchemas.app.tableRow row = null;

	if (test.Rows.Count &gt; 0)
	{
		row = (DataSchemas.app.tableRow)test.Rows[0];
	}

} finally {
	de.Close();
}
{% endhighlight %}

<p>and this for weakly typed datasets:</p>

{% highlight csharp %}
MySql.Data.MySqlClient.MySqlCommand cmd = new MySql.Data.MySqlClient.MySqlCommand("SELECT * FROM table WHERE blah=@blah");
cmd.Parameters.Add("@blah", "test");

Tools.DataExecutor de = new Tools.DataExecutor(cmd, false);

DataSet ds = new DataSet();

de.Adapter.Fill(ds);
{% endhighlight %}

<p>Easy eh? :)</p>
<p>The parameterization of the queries will protect you against SQL Injection exploits so I'd recommend you do that at all times. Your connection string should go in your Web.Config file and then be specified inside the DataExecutor class. It's worth pointing out that if you don't set oldsyntax=true; then you must ensure that you use ? for your parameter names as opposed to @.</p>





