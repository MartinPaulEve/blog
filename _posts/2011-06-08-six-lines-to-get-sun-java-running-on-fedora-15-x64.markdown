---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Six lines to get Sun Java running on Fedora 15 x64
wordpress_id: 1146
wordpress_url: https://www.martineve.com/?p=1146
date: !binary |-
  MjAxMS0wNi0wOCAxMTozNDowOSArMDIwMA==
date_gmt: !binary |-
  MjAxMS0wNi0wOCAxMTozNDowOSArMDIwMA==
categories:
- Technology
- Linux
tags:
- Linux
- Java
- Fedora
comments:
- id: 6511
  author: DerZauberer
  author_email: info@dh-online.net
  author_url: http://dh-online.net
  date: !binary |-
    MjAxMS0wNy0yNiAxODo0ODowMCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNy0yNiAxODo0ODowMCArMDIwMA==
  content: Wouldn't it be better to use /usr/java/latest/ instead of the version number?
- id: 6527
  author: Jp Delamarre
  author_email: jp.delamarre@free.fr
  author_url: ''
  date: !binary |-
    MjAxMS0wOS0wNCAxOTo0MjowMCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wOS0wNCAxOTo0MjowMCArMDIwMA==
  content: ! 'bash: java: command not found... when I ue on Fedora 15'
- id: 6528
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  date: !binary |-
    MjAxMS0wOS0wNCAxOTo0MzowMCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wOS0wNCAxOTo0MzowMCArMDIwMA==
  content: Re-logged in? Does /usr/bin/java work? Post output from install.
doi: "https://doi.org/10.59348/nhy1y-n0y17"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/06/08/six-lines-to-get-sun-java-running-on-fedora-15-x64"
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





