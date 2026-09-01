---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/05/21/bypassing-same-origin-policy-using-mash-ups
categories:
- Information Security
comments: []
date: 2007-05-21 14:23:44 +0200
date_gmt: 2007-05-21 14:23:44 +0200
doi: https://doi.org/10.59348/g5rvx-tmr98
roguescholar: https://rogue-scholar.org/records/c6m0f-0m171
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mnp4lhu2h
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- information security
- XSS
title: Bypassing Same Origin Policy using Mash-Ups
wordpress_id: 280
wordpress_url: http://pro.grammatic.org/post-bypassing-same-origin-policy-using-mashups-19.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mnp4lhu2h"
---

<p><a href="http://www.gnucitizen.org" title="GNUZITIZEN's blog">GNUCITIZEN</a> has been going on about this for some time now, but the truly devastating impact of what he has been saying only actually hit me today when reading about his <a href="http://www.gnucitizen.org/ghdb/">JavaScript interface</a> to <a href="http://johnny.ihackstuff.com/ghdb.php" title="Johnny's Google Hacking Database">Johnny's Google Hacking Database</a>.</p>
<p>The scenario is as follows. The interface contains NO SERVER SIDE SCRIPTS and no iframes or other such methods for loading offsite data but instead utilises the JSON data format to include remote script files. GC's example uses <a href="http://www.dapper.net/" title="Dapper the Data Mapper">Dapper</a> to perform the remote data retrieval in JSON format and then loads it into a script tag. For example:</p>

{% highlight html %}
	<script src="http://www.dapper.net/transform.php?dappName=GoogleHackingDatabaseCategoriesReader&amp;transformer=JSON&amp;

	extraArg_callbackFunctionWrapper=json_1179755998729&amp;applyToUrl=http%3A%2F%2Fjohnny.ihackstuff.com%2Fghdb.php" type="text/javascript"></script>
{% endhighlight %}

<p>This loads the contents of the Google Hacking Database into a JavaScript object which can then be parsed. Essentially this is remote data retrieval entirely from JavaScript. If services like Dapper continue to develop (for example to allow access to an exact URL and return the output in JSON format) then the Same Origin Policy is history.</p>