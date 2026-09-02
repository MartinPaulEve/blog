---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2008/07/31/c-dataexecutor-class-again
categories:
- Programming
comments: []
date: 2008-07-31 07:33:04 +0200
date_gmt: 2008-07-31 07:33:04 +0200
doi: https://doi.org/10.59348/ker7b-4sd65
roguescholar: https://rogue-scholar.org/records/jnqwv-g6a96
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmpfvrq2f
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- C#
- MySQL
- Unit Testing
title: C# DataExecutor class again
wordpress_id: 250
wordpress_url: http://pro.grammatic.org/post-c-dataexecutor-class-again-52.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmpfvrq2f"
kcworks: https://works.hcommons.org/records/azhqj-gn104
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