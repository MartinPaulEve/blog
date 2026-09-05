---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/04/03/installing-zotero-on-ubuntu-natty-11-04beta
categories:
- Linux
comments:
- author: Leigh Honeywell
  author_email: leigh@hypatia.ca
  author_url: http://hypatia.ca
  content: "Hey, thanks for posting this - I was struggling with all sorts of bizarro
    errors in Ubuntu 10.10 and OO 3.2 and rolling back the Zotero extension totally
    fixed it.  My grades and sleep schedule thank you :)\r\n\r\n-Leigh"
  date: 2011-04-05 07:08:44 +0200
  date_gmt: 2011-04-05 07:08:44 +0200
  id: 6273
- author: chris
  author_email: christiankroy@gmail.com
  author_url: ''
  content: "Struggled all morning with getting Zotero|Firefox|LibreWriter working.\r\n\r\nThis
    worked for me.  \r\nThank you so much!"
  date: 2011-04-28 16:54:12 +0200
  date_gmt: 2011-04-28 16:54:12 +0200
  id: 6287
- author: Martijn
  author_email: martijn@monomania.nl
  author_url: ''
  content: Thanks. I already wondered why Zotero left me. This one worked just fine
    for me.
  date: 2011-05-11 20:42:26 +0200
  date_gmt: 2011-05-11 20:42:26 +0200
  id: 6292
- author: friso
  author_email: mailfriso@yahoo.com
  author_url: ''
  content: "i changed\r\n\r\nsudo update-alternatives –config java\r\n\r\nto\r\n\r\nsudo
    update-alternatives --config java"
  date: 2011-05-15 19:41:09 +0200
  date_gmt: 2011-05-15 19:41:09 +0200
  id: 6295
- author: friso
  author_email: mailfriso@yahoo.com
  author_url: ''
  content: yep, Zotero's up and running again!
  date: 2011-05-16 04:43:21 +0200
  date_gmt: 2011-05-16 04:43:21 +0200
  id: 6296
- author: roney
  author_email: roneyfraga@gmail.com
  author_url: ''
  content: Muito obrigado!
  date: 2011-09-19 14:39:00 +0200
  date_gmt: 2011-09-19 14:39:00 +0200
  id: 6537
- author: PN
  author_email: tem_nao@hotmail.com
  author_url: ''
  content: merci !!!!
  date: 2012-04-12 22:08:04 +0200
  date_gmt: 2012-04-12 22:08:04 +0200
  id: 6687
date: 2011-04-03 13:56:34 +0200
date_gmt: 2011-04-03 13:56:34 +0200
doi: https://doi.org/10.59348/nznr5-3xc06
roguescholar: https://rogue-scholar.org/records/4z2bh-9vw64
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mkhkmlj2e
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- zotero
- Linux
- Ubuntu
- Natty
title: Installing Zotero on Ubuntu Natty (11.04/Beta)
wordpress_id: 924
wordpress_url: https://www.martineve.com/?p=924
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mkhkmlj2e"
kcworks: https://works.hcommons.org/records/aek2d-hb668
references:
- http://archive.canonical.com/ubuntu # Canonical Ubuntu archive repository
- http://www.zotero.org/ # Zotero reference manager main site
- http://www.zotero.org/download/integration/Zotero-OpenOffice-Plugin-3.1b1.xpi # Zotero OpenOffice plugin 3.1b1 download
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