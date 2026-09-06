---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2009/06/23/installing-office-2007-on-wine-1-1-24
categories:
- Linux
comments: []
date: 2009-06-23 02:51:49 +0200
last_modified_at: 2026-09-06
date_gmt: 2009-06-23 02:51:49 +0200
doi: https://doi.org/10.59348/11p8j-59870
roguescholar: https://rogue-scholar.org/records/yzkc8-pyb20
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmjva7m2i
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Linux
- wine
- Microsoft Office
- install
title: Installing Office 2007 on wine 1.1.24
wordpress_id: 234
wordpress_url: http://pro.grammatic.org/post-installing-office-2007-on-wine-1124-68.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmjva7m2i"
kcworks: https://works.hcommons.org/records/qpqka-x7144
references:
- title: Index of /ubuntu-wine/ppa/ubuntu
  type: WebPage
  url: http://ppa.launchpad.net/ubuntu-wine/ppa/ubuntu
- http://www.kegel.com/wine/winetricks # winetricks script by kegel
---

<p>The latest version of Wine (as of 2009-06-23: wine-1.1.24) fixes an important regression that makes it far far easier to install Microsoft Office 2007 on Wine. I personally never use any of the Office suite for anything except ensuring that the documents that I export from OpenOffice for Word users look acceptable and professional.</p>
<p>While the suggestions of the Wine website state that it is possible on 1.1.3 to just run the installer, on 1.1.24, there's a few tweaks that will make the process go smoothly.</p>
<p>First of all, ensure you have the latest version. In (K)Ubuntu you'll want to add the PPAs:</p>
<blockquote><p>
deb http://ppa.launchpad.net/ubuntu-wine/ppa/ubuntu jaunty main<br/><br />
deb-src http://ppa.launchpad.net/ubuntu-wine/ppa/ubuntu jaunty main
</p></blockquote>
<p>and then add the correct GPG keys:</p>
<blockquote><p>sudo apt-key adv --recv-keys --keyserver keyserver.ubuntu.com F9CB8DB0</p></blockquote>
<p>Obviously you'll then need to:</p>
<blockquote><p>
sudo apt-get update<br/><br />
sudo apt-get upgrade
</p></blockquote>
<p>When this is all done, go to a command prompt and type:</p>
<blockquote><p>winecfg</p></blockquote>
<p>In the resulting dialogue that appears, make sure the operating system is set to <strong>Windows Vista</strong>.</p>
<p>Now, browse to your CD drive and run Setup.exe on the Office 2007 disc. You could also do this in a command prompt; something like:</p>
<blockquote><p>
wine /media/cdrom0/Setup.exe
</p></blockquote>
<p>Go through the installation and all should be well!</p>
<p>Now, grab a copy of winetricks and install the necessary components (I always install components in this order as it seems to not prompt me to reboot):</p>
<blockquote><p>
wget http://www.kegel.com/wine/winetricks <br/><br />
sh winetricks vcrun2005sp1<br/><br />
sh winetricks dotnet20<br/><br />
sh winetricks msxml3 gdiplus riched20 riched30
</p></blockquote>
<p>Finally, go back into <strong>winecfg</strong> and switch the operating system to <strong>Windows XP</strong>. Tada! It should all work!</p>