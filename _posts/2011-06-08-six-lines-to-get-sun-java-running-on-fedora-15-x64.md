---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/06/08/six-lines-to-get-sun-java-running-on-fedora-15-x64
categories:
- Linux
comments:
- author: DerZauberer
  author_email: info@dh-online.net
  author_url: http://dh-online.net
  content: Wouldn't it be better to use /usr/java/latest/ instead of the version number?
  date: 2011-07-26 18:48:00 +0200
  date_gmt: 2011-07-26 18:48:00 +0200
  id: 6511
- author: Jp Delamarre
  author_email: jp.delamarre@free.fr
  author_url: ''
  content: 'bash: java: command not found... when I ue on Fedora 15'
  date: 2011-09-04 19:42:00 +0200
  date_gmt: 2011-09-04 19:42:00 +0200
  id: 6527
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  content: Re-logged in? Does /usr/bin/java work? Post output from install.
  date: 2011-09-04 19:43:00 +0200
  date_gmt: 2011-09-04 19:43:00 +0200
  id: 6528
date: 2011-06-08 11:34:09 +0200
date_gmt: 2011-06-08 11:34:09 +0200
doi: https://doi.org/10.59348/nhy1y-n0y17
roguescholar: https://rogue-scholar.org/records/evmsj-0p297
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mkc5pf72p
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Linux
- Java
- Fedora
title: Six lines to get Sun Java running on Fedora 15 x64
wordpress_id: 1146
wordpress_url: https://www.martineve.com/?p=1146
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mkc5pf72p"
kcworks: https://works.hcommons.org/records/15cj1-cd029
references:
- http://www.if-not-true-then-false.com/2010/install-sun-oracle-java-jdk-jre-7-on-fedora-centos-red-hat-rhel/ # Guide to install Sun Oracle Java on Fedora/CentOS
- http://download.oracle.com/otn-pub/java/jdk/6u25-b06/jre-6u25-linux-x64-rpm.bin # Oracle JRE 6u25 Linux x64 RPM download
---

<p>Here's a quick 'n' easy version of <a href="http://www.if-not-true-then-false.com/2010/install-sun-oracle-java-jdk-jre-7-on-fedora-centos-red-hat-rhel/">another post</a> that uses the rpm instead of the extracting to opt.</p>

{% highlight bash %}
wget http://download.oracle.com/otn-pub/java/jdk/6u25-b06/jre-6u25-linux-x64-rpm.bin
chmod +x jre-*
sudo ./jre-*
sudo alternatives --install /usr/bin/java java /usr/java/jre1.6.0_25/bin/java 20000
sudo alternatives --install /usr/bin/javaws javaws /usr/java/jre1.6.0_25/bin/javaws 20000
sudo alternatives --install /usr/lib64/mozilla/plugins/libjavaplugin.so libjavaplugin.so.x86_64 /usr/java/jre1.6.0_25/lib/amd64/libnpjp2.so 20000
{% endhighlight %}

<p>Enjoy.</p>