---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/05/15/javascript-eval-string-fromcharcode-encoder
categories:
- Information Security
comments: []
date: 2007-05-15 18:49:09 +0200
last_modified_at: 2026-09-06
date_gmt: 2007-05-15 18:49:09 +0200
doi: https://doi.org/10.59348/29wts-5q506
roguescholar: https://rogue-scholar.org/records/t1ge5-6hp47
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mnt4cg22r
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- information security
title: JavaScript eval String.fromCharCode encoder
wordpress_id: 288
wordpress_url: http://pro.grammatic.org/post-javascript-eval-stringfromcharcode-encoder-11.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mnt4cg22r"
kcworks: https://works.hcommons.org/records/c871j-cwx53
references:
- http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd # W3C XHTML 1.0 Transitional DTD
---

<p>Here is a nice tool for encoding JavaScript into eval(String.fromCharCode(x,x,x)) format. A full HTML page is listed here, or you can try it out live at the bottom of this post.</p>

{% highlight html %}
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
	<title>Javascript Eval Encoder</title>
	<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1"/>
	<script type="text/javascript">
		function encode_to_javascript() {
			var input = document.getElementById('inputtext').value;

			var output = 'eval(String.fromCharCode(';

			for(pos = 0; pos < input.length; pos++) {
				output += input.charCodeAt(pos);
	
				if(pos != (input.length - 1)) {
					output += ",";
				}
			}

			output += '))';

			document.getElementById('result').innerHTML = output;
			return 0;
		}
	</script>
	</head>
	<body>
		<textarea id="inputtext" rows="10" cols="50"></textarea><br/>
		<input type="submit" value="Encode" onclick="javascript:encode_to_javascript()"/>
		<br/><span id="result"></span>
	</body>
</html>
{% endhighlight %}

<p><script type="text/javascript">eval(String.fromCharCode(102,117,110,99,116,105,111,110,32,101,110,99,111,100,101,95,116,111,95,106,97,118,97,115,99,114,105,112,116,40,41,32,123,32,118,97,114,32,105,110,112,117,116,32,61,32,100,111,99,117,109,101,110,116,46,103,101,116,69,108,101,109,101,110,116,66,121,73,100,40,39,105,110,112,117,116,116,101,120,116,39,41,46,118,97,108,117,101,59,32,118,97,114,32,111,117,116,112,117,116,32,61,32,39,101,118,97,108,40,83,116,114,105,110,103,46,102,114,111,109,67,104,97,114,67,111,100,101,40,39,59,32,102,111,114,40,112,111,115,32,61,32,48,59,32,112,111,115,32,60,32,105,110,112,117,116,46,108,101,110,103,116,104,59,32,112,111,115,43,43,41,32,123,32,111,117,116,112,117,116,32,43,61,32,105,110,112,117,116,46,99,104,97,114,67,111,100,101,65,116,40,112,111,115,41,59,32,105,102,40,112,111,115,32,33,61,32,40,105,110,112,117,116,46,108,101,110,103,116,104,32,45,32,49,41,41,32,123,32,111,117,116,112,117,116,32,43,61,32,34,44,34,59,32,125,32,125,32,111,117,116,112,117,116,32,43,61,32,39,41,41,39,59,32,100,111,99,117,109,101,110,116,46,103,101,116,69,108,101,109,101,110,116,66,121,73,100,40,39,114,101,115,117,108,116,39,41,46,105,110,110,101,114,72,84,77,76,32,61,32,111,117,116,112,117,116,59,32,114,101,116,117,114,110,32,48,59,32,125))</script></p>
<p><textarea id="inputtext" rows="10" cols="50">alert('test');</textarea></p>
<p><a onclick="javascript:encode_to_javascript()">Encode</a><br />
<br/><br />
<span id="result"></span></p>