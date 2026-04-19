---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: C# DataExecutor class again
wordpress_id: 250
wordpress_url: http://pro.grammatic.org/post-c-dataexecutor-class-again-52.aspx
date: !binary |-
  MjAwOC0wNy0zMSAwNzozMzowNCArMDIwMA==
date_gmt: !binary |-
  MjAwOC0wNy0zMSAwNzozMzowNCArMDIwMA==
categories:
- Technology
- .NET
tags:
- C#
- MySQL
- Unit Testing
comments: []
doi: "https://doi.org/10.59348/ker7b-4sd65"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2008/07/31/c-dataexecutor-class-again"
---
<p>Just been asked some further questions about the <a href="http://www.martineve.com/2007/06/26/c-dataexecutor-class-available/">DataExecutor</a> class on FreeNode and thought I'd give some usage instructions/clarification here.</p>
<p>Howto: Fill a strongly typed dataset</p>
<p>Set your base class (of your TableAdapter) to Tools.genericTableAdapter.<br/><br />
Fill your strongly typed DataSet thus:</p>

{% highlight csharp %}
	DataExecutor de = null;

	try{
		de = new DataExecutor();
	
		const string TABLEPREFIX = "blog";
	
		MySqlCommand cmd = new MySqlCommand(string.Format("SELECT * FROM {0} WHERE id=@id", TABLEPREFIX));
		cmd.Parameters.AddWithValue("@id", id);
            
		de.NextCommand(cmd, false);

		DataSchema.blog_postsDataTable postsDT = new DataSchema.blog_postsDataTable();

		DataTable dtRef = (DataTable)postsDT;

		de.DataSetSchema(ref dtRef);
	} finally {
		if(de != null) de.Close();
	}
{% endhighlight %}

<p>Why do it like this?</p>
<p>Answer: because it lets you hook into the return results for testing purposes.</p>

{% highlight csharp %}
de = new Tools.DataExecutor(true);
de.OnTestModeFill += new Tools.DataExecutor.TestModeFillInterceptor(taskFillHandler);
{% endhighlight %}

<p>Then in taskFillHandler you will receive a reference to a DataTable that you can populate in whatever way you like to ensure that your application behaves correctly - aka. offline database unit testing!</p>





