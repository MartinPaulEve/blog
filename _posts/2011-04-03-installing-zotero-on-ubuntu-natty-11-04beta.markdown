---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Installing Zotero on Ubuntu Natty (11.04/Beta)
wordpress_id: 924
wordpress_url: https://www.martineve.com/?p=924
date: !binary |-
  MjAxMS0wNC0wMyAxMzo1NjozNCArMDIwMA==
date_gmt: !binary |-
  MjAxMS0wNC0wMyAxMzo1NjozNCArMDIwMA==
categories:
- Technology
- Linux
tags:
- zotero
- Linux
- Ubuntu
- Natty
comments:
- id: 6273
  author: Leigh Honeywell
  author_email: leigh@hypatia.ca
  author_url: http://hypatia.ca
  date: !binary |-
    MjAxMS0wNC0wNSAwNzowODo0NCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNC0wNSAwNzowODo0NCArMDIwMA==
  content: ! "Hey, thanks for posting this - I was struggling with all sorts of bizarro
    errors in Ubuntu 10.10 and OO 3.2 and rolling back the Zotero extension totally
    fixed it.  My grades and sleep schedule thank you :)\r\n\r\n-Leigh"
- id: 6287
  author: chris
  author_email: christiankroy@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wNC0yOCAxNjo1NDoxMiArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNC0yOCAxNjo1NDoxMiArMDIwMA==
  content: ! "Struggled all morning with getting Zotero|Firefox|LibreWriter working.\r\n\r\nThis
    worked for me.  \r\nThank you so much!"
- id: 6292
  author: Martijn
  author_email: martijn@monomania.nl
  author_url: ''
  date: !binary |-
    MjAxMS0wNS0xMSAyMDo0MjoyNiArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNS0xMSAyMDo0MjoyNiArMDIwMA==
  content: Thanks. I already wondered why Zotero left me. This one worked just fine
    for me.
- id: 6295
  author: friso
  author_email: mailfriso@yahoo.com
  author_url: ''
  date: !binary |-
    MjAxMS0wNS0xNSAxOTo0MTowOSArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNS0xNSAxOTo0MTowOSArMDIwMA==
  content: ! "i changed\r\n\r\nsudo update-alternatives –config java\r\n\r\nto\r\n\r\nsudo
    update-alternatives --config java"
- id: 6296
  author: friso
  author_email: mailfriso@yahoo.com
  author_url: ''
  date: !binary |-
    MjAxMS0wNS0xNiAwNDo0MzoyMSArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNS0xNiAwNDo0MzoyMSArMDIwMA==
  content: yep, Zotero's up and running again!
- id: 6537
  author: roney
  author_email: roneyfraga@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wOS0xOSAxNDozOTowMCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wOS0xOSAxNDozOTowMCArMDIwMA==
  content: Muito obrigado!
- id: 6687
  author: PN
  author_email: tem_nao@hotmail.com
  author_url: ''
  date: !binary |-
    MjAxMi0wNC0xMiAyMjowODowNCArMDIwMA==
  date_gmt: !binary |-
    MjAxMi0wNC0xMiAyMjowODowNCArMDIwMA==
  content: merci !!!!
doi: "https://doi.org/10.59348/nznr5-3xc06"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/04/03/installing-zotero-on-ubuntu-natty-11-04beta"
---
<div>I've been playing with the new setup of Unity on Ubuntu Natty 11.04 beta, which now comes preloaded with the forked LibreOffice. This has caused some problems for installation of Zotero, so I want to here give the walkthrough instructions that I used in a LiveCD environment to get everything working.</p>
<p><img src="https://www.martineve.com/wp-content/uploads/2011/04/Natty-Wallpaper.png" alt="Ubuntu Natty" title="Ubuntu Natty" width="334" height="224" class="alignnone size-full wp-image-926" style="margin-top:0px;" /><i>Featured image by <a href="https://profiles.google.com/Kirby.WA/about">Wyatt Kirby</a> with unspecified copyright or licensing provisions. Used here in good faith and for no commercial gain to demonstrate the operating system referred to. If you own the copyright to this image and would like it removed, please contact me and I will remove it ASAP.</i>
</div>
<hr/>
1.) Add the Maverick partner repository:</p>
<p>Software Center -> Edit Menu -> Software Sources -> Other sources -> Add:</p>
<p>deb http://archive.canonical.com/ubuntu maverick partner</p>
<p>2.) Drop to a command prompt:</p>
<blockquote><p>sudo apt-get update<br />
sudo apt-get install sun-java6-jre sun-java6-plugin<br />
sudo update-alternatives --config java</p></blockquote>
<p>If the last option prompts you to set a specific java configuration, ensure you select the Sun variant.</p>
<p>3.) Install Zotero plugin from <a href="http://www.zotero.org/">http://www.zotero.org/</a></p>
<p>4.) Install the outdated OpenOffice plugin, not the most recent one: <a href="http://www.zotero.org/download/integration/Zotero-OpenOffice-Plugin-3.1b1.xpi">http://www.zotero.org/download/integration/Zotero-OpenOffice-Plugin-3.1b1.xpi</a></p>
<p>5.) After Firefox has restarted go to Zotero -> Preferences -> Cite tab.</p>
<p>In here, change the OpenOffice parameters to the following:</p>
<p>UNO: file:///usr/lib/libreoffice/basis-link/ure-link/share/java/<br />
soffice binary: file:///usr/lib/libreoffice/program/</p>
<p>6.) Click "install plugin".</p>
<p>If this fails, go into LibreOffice, Tools menu -> Extension manager -> Add</p>
<p>Navigate to your firefox profile directory which will look like:</p>
<p>/home/yourusername/.mozilla/firefox/ALONGSTRINGOFLETTERS/extensions/zoteroOpenOfficeIntegration@zotero.org/install/</p>
<p>and manually add the .oxt file from within.</p>
<p>With any luck, you should be set. Worth also checking in LibreOffice -> Edit menu -> Preferences -> Java that you are using the Sun interpreter in LibreOffice.</p>





