---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/05/01/running-zotero-on-ubuntu-lucid
categories:
- Linux
comments: []
date: 2010-05-01 18:31:00 +0200
date_gmt: 2010-05-01 18:31:00 +0200
doi: https://doi.org/10.59348/ktbh3-ddn88
roguescholar: https://rogue-scholar.org/records/hczrf-jev59
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mm6vngt2e
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- zotero
title: Running Zotero on Ubuntu Lucid
wordpress_id: 17
wordpress_url: http://new.martineve.com/?p=17
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mm6vngt2e"
kcworks: https://works.hcommons.org/records/5t6f9-hdj93
references:
- title: Zotero in Ubuntu 10.4 Lucid Lynx
  type: WebPage
  url: http://forums.zotero.org/discussion/11429/zotero-in-ubuntu-104-lucid-lynx/
  isPartOf:
    name: Zotero Forums
    type: WebSite
- http://archive.canonical.com/ubuntu # Canonical Ubuntu package archive
---

<p>I have just upgraded my work machine (laptop) to Kubuntu Lucid Lynx (10.4) and have to say that I was mightily impressed with the ease of upgrade; 99% flawless.
 The one area where I did experience some difficulty was in running Zotero: Zotero Integration Error blared at me whenever I tried to add a citation.
 Fortunately, I had encountered this before and knew it was a problem regarding OpenJDK and IceTea. Indeed, a quick google search turned up <a href="http://forums.zotero.org/discussion/11429/zotero-in-ubuntu-104-lucid-lynx/">the answer</a>, which I will quote here, with minor alterations to account for the final versions.
 Open up a terminal and type, line by line:
<p /></p>
<blockquote><p>
sudo bash<br />
sudo echo 'deb <a href="http://archive.canonical.com/ubuntu" rel="nofollow">http://archive.canonical.com/ubuntu</a> lucid partner' &gt;&gt; /etc/apt/sources.list<br />
exit<br />
sudo apt-get update<br />
sudo apt-get install sun-java6-bin sun-java6-jre sun-java6-plugin<br />
sudo update-alternatives --config java<br />
sudo ln -s /usr/lib/jvm/java-6-sun/jre/lib/i386/libnpjp2.so  /usr/lib/mozilla/plugins/</p></blockquote><br />
<p> Go into OpenOffice. Go to Tools -&gt; Options -&gt; Java and select the Sun 1.6.0.20 runtime. Close OpenOffice.
 Then, in Firefox go to Tools -&gt; Add-Ons. Go to Zotero OpenOffice Integration and click Preferences. Reinstall the OpenOffice extensions from there.
 Fire everything up and you should be up and running!</p>