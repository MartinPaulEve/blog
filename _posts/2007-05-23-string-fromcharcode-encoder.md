---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2007/05/23/string-fromcharcode-encoder
categories:
- Information Security
comments:
- author: XSS Tutorial | Martin Paul Eve
  author_email: ''
  author_url: http://www.martineve.com/2007/05/23/xss-tutorial/
  content: '[...] cand. at the University of Sussex    Skip to content HomeAboutCurriculum
    VitaeProfile              &larr; String.fromCharCode Encoder (C)SRF one-time token
    bypass using AJAX and XSS [...]'
  date: 2010-11-07 13:17:31 +0100
  date_gmt: 2010-11-07 13:17:31 +0100
  id: 190
date: 2007-05-23 16:51:40 +0200
date_gmt: 2007-05-23 16:51:40 +0200
doi: https://doi.org/10.59348/7s19g-84e41
roguescholar: https://rogue-scholar.org/records/djjr1-7tz87
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mno7ewq2f
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- information security
- Javascript
- Encoder
title: String.fromCharCode Encoder
wordpress_id: 279
wordpress_url: http://pro.grammatic.org/post-stringfromcharcode-encoder-21.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mno7ewq2f"
kcworks: https://works.hcommons.org/records/zve2f-qx071
---

<p>Enter JavaScript in the box below and press "encode":<br/></p>
<p><script type="text/javascript">eval(String.fromCharCode(102,117,110,99,116,105,111,110,32,101,110,99,111,100,101,95,116,111,95,106,97,118,97,115,99,114,105,112,116,40,41,32,123,32,118,97,114,32,105,110,112,117,116,32,61,32,100,111,99,117,109,101,110,116,46,103,101,116,69,108,101,109,101,110,116,66,121,73,100,40,39,105,110,112,117,116,116,101,120,116,39,41,46,118,97,108,117,101,59,32,118,97,114,32,111,117,116,112,117,116,32,61,32,39,101,118,97,108,40,83,116,114,105,110,103,46,102,114,111,109,67,104,97,114,67,111,100,101,40,39,59,32,102,111,114,40,112,111,115,32,61,32,48,59,32,112,111,115,32,60,32,105,110,112,117,116,46,108,101,110,103,116,104,59,32,112,111,115,43,43,41,32,123,32,111,117,116,112,117,116,32,43,61,32,105,110,112,117,116,46,99,104,97,114,67,111,100,101,65,116,40,112,111,115,41,59,32,105,102,40,112,111,115,32,33,61,32,40,105,110,112,117,116,46,108,101,110,103,116,104,32,45,32,49,41,41,32,123,32,111,117,116,112,117,116,32,43,61,32,34,44,34,59,32,125,32,125,32,111,117,116,112,117,116,32,43,61,32,39,41,41,39,59,32,100,111,99,117,109,101,110,116,46,103,101,116,69,108,101,109,101,110,116,66,121,73,100,40,39,114,101,115,117,108,116,39,41,46,105,110,110,101,114,72,84,77,76,32,61,32,111,117,116,112,117,116,59,32,114,101,116,117,114,110,32,48,59,32,125))</script></p>
<p><textarea id="inputtext" rows="10" cols="50">alert('test');</textarea></p>
<p><a onclick="javascript:encode_to_javascript()">Encode</a><br />
<br/><br />
<span id="result"></span></p>