---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/05/15/javascript-referer-scripts-xss-injection
categories:
- Technology
- InfoSec
comments: []
date: 2007-05-15 13:52:06 +0200
date_gmt: 2007-05-15 13:52:06 +0200
doi: https://doi.org/10.59348/877mz-7q690
image:
  feature: geek.png
layout: post
ogImage: geek.png
published: true
status: publish
tags:
- information security
- mod_rewrite
- XSS
title: JavaScript Referer Scripts XSS Injection
wordpress_id: 293
wordpress_url: http://pro.grammatic.org/post-javascript-referer-scripts-xss-injection-5.aspx
---

<p>Many sites use JavaScript methods to inject a hidden form field into 404 pages to trace the original page that points to the invalid link. An example of this can be found at <a href="http://www.yaldex.com/FSPageDetails/_404Referrer.htm">http://www.yaldex.com/FSPageDetails/_404Referrer.htm</a>. The attentive observer will spot that this method of writing the field injects the HTTP referrer directly into the page without any sanitization.</p>
<p>So what? It is very difficult to forge referrers from a malicious website, however, with the help of the mod_rewrite apache module it is possible to create referrer strings which contain malicious strings.</p>
<p>
The process for exploitation is as follows:</p>
<ol>
<li>Create a .htaccess file that specifies a mod rewrite that includes a capture. For example: RewriteRule XSSReferer/(.+)$ /xss_test_referer.htm. This will forward all requests to the XSSReferer directory to xss_test_referer.htm GÇô in this case a page with a link to the target. Note that because mod_rewrite is used the referrer is NOT xss_test_referer.htm but the originally entered url.</li>
<li>Visit the virtual RewriteRule with a malicious string. An example for IE7 is <a href="http://www.md5-db.com/XSSReferer/'style=xx:expression(alert(1));othervar='">http://www.md5-db.com/XSSReferer/'style=xx:expression(alert(1));othervar='</a> which will display a standard XSS test and probably crash your browser.</li>
</ol>
<p>
Note that this is far harder to exploit in Firefox. This is because of the way the URLs are encoded, making it very difficult to inject anything other than a style tag and, as mentioned in my previous post, Firefox does not yet support loading of XBL documents without a fragment identifier.</p>
<p>To protect against this type of injection you should always filter ANY input passed directly to the page... even HTTP headers.</p>