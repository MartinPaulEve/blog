---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Using Elliptical Curve Cryptography in OpenSSH
wordpress_id: 1329
wordpress_url: https://www.martineve.com/?p=1329
date: !binary |-
  MjAxMS0wNy0yMiAxNTo0OToxNSArMDIwMA==
date_gmt: !binary |-
  MjAxMS0wNy0yMiAxNTo0OToxNSArMDIwMA==
categories:
- Technology
- InfoSec
- Linux
tags:
- information security
- ssh
- cryptography
- security
comments:
- id: 6514
  author: Efendi
  author_email: efendi@informatika.lipi.go.id
  author_url: ''
  date: !binary |-
    MjAxMS0wOC0wMyAwNzozODowMCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wOC0wMyAwNzozODowMCArMDIwMA==
  content: ! 'I used Fedora 15 to create ecdsa as like as your inctructions, but that
    still cannot created ecdsa key pair..
    What I have suppose to do?, Please help me and thank!'
- id: 6515
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  date: !binary |-
    MjAxMS0wOC0wMyAwNzo0MjowMCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wOC0wMyAwNzo0MjowMCArMDIwMA==
  content: Did you install OpenSSL from source as instructed? Paste the output of
    your OpenSSH ./configure.
- id: 6518
  author: Efendi
  author_email: efendi@informatika.lipi.go.id
  author_url: ''
  date: !binary |-
    MjAxMS0wOC0wNCAwODowNjowMCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wOC0wNCAwODowNjowMCArMDIwMA==
  content: ! 'Not yet It was, but after I do reinstalling OpenSSL with source that
    U recommended. I got this statement when I had compiled command ./configure from
    OpenSSH :
    [root@XXXXXX openssh-5.8p2]# ./configure --with-selinux --bindir=/usr/bin --sbindir=/usr/sbin
    --with-ssl-dir=/usr/local/ssl/
    checking for gcc... gcc
    checking for C compiler default output file name... a.out
    checking whether the C compiler works... yes
    checking whether we are cross compiling... no
    ...
    checking zlib.h presence... no
    checking for zlib.h... no
    configure: error: *** zlib.h missing - please install first or check config.log
    ***
    [root@XXXXXX openssh-5.8p2]#
    What should I do now? thank 4 Ur help!
'
- id: 6519
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  date: !binary |-
    MjAxMS0wOC0wNCAwODoxOTowMCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wOC0wNCAwODoxOTowMCArMDIwMA==
  content: ! "You need to install the packages that provide zlib.h.\n\nTry (as root):\n\nyum
    groupinstall \"Development Tools\"\n\nand\n\nyum install kernel-devel.x86_64\n
    (if running on 64 bit -- otherwise not entirely sure of package name)"
- id: 6520
  author: Efendi
  author_email: efendi@informatika.lipi.go.id
  author_url: ''
  date: !binary |-
    MjAxMS0wOC0wNCAwODo1MjowMCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wOC0wNCAwODo1MjowMCArMDIwMA==
  content: ! 'I''m already solve for zlib problem but in ./configure i got "checking
    for selinux/selinux.h... no
    configure: error: SELinux support requires selinux.h header"... Do you have opinion,
    sir?'
- id: 6521
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  date: !binary |-
    MjAxMS0wOC0wNCAwOToyNjowMCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wOC0wNCAwOToyNjowMCArMDIwMA==
  content: ! 'Try:
    yum install libselinux-devel'
- id: 6523
  author: Efendi
  author_email: efendi@informatika.lipi.go.id
  author_url: ''
  date: !binary |-
    MjAxMS0wOC0wNSAwMjowODowMCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wOC0wNSAwMjowODowMCArMDIwMA==
  content: Thank a lot for your help. At now i can continue my works.
doi: "https://doi.org/10.59348/dz3dw-gxh20"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/07/22/using-elliptical-curve-cryptography-in-openssh"
---
<p>Having read <a href="http://lackof.org/taggart/hacking/ssh/">two great posts</a> on <a href="http://pthree.org/?p=1930">OpenSSH best practices</a>, I decided today that I wanted to upgrade my SSH key architecture to use <a href="http://pthree.org/2011/02/17/elliptic-curve-cryptography-in-openssh/">Elliptical Curve Cryptography</a>. There were several gotchas involved that I thought it would be worth sharing here. There are, at the time of writing, no packages for Fedora 15 or Debian stable that I could find, so I've worked from source.</p>
<p>Getting ECC working on some systems can be a bit of a pain. Fedora, in particular, has decided, due to patent encumbrance, to remove the header include files for OpenSSL's ECC implementation. To get around this, I therefore recommend <a href="http://www.openssl.org/source/">reinstalling OpenSSL from source</a> from their site. You will be able to tell whether your distro will have this problem because, in the ./configure output of OpenSSH you will encounter:</p>
<blockquote><p>checking whether OpenSSL has complete ECC support... no</p></blockquote>
<p>An easy way to check is to look for the presence of /usr/include/openssl/ecdsa.h</p>
<p>So, once you've got the latest and greatest OpenSSL installed, download the latest <a href="http://ftp.plig.net/pub/OpenBSD/OpenSSH/portable/openssh-5.8p2.tar.gz">OpenSSH portable tar.gz</a>. Then, you'll want to run the following.</p>
<p>On Fedora 15 (after installing OpenSSL from source; last command in this list needs to be root):</p>

{% highlight bash %}
tar -xzf openssh-5.8p2.tar.gz
cd openssh-5.8p2
./configure --with-selinux --bindir=/usr/bin --sbindir=/usr/sbin --with-ssl-dir=/usr/local/ssl/
make
make install
{% endhighlight %}

<p>On Debian/Ubuntu (not necessary to install OpenSSL from source):</p>

{% highlight bash %}
tar -xzf openssh-5.8p2.tar.gz
cd openssh-5.8p2
./configure --bindir=/usr/bin --sbindir=/usr/sbin
make
sudo make install
{% endhighlight %}

<p>You can then use the setup as expected.</p>

{% highlight bash %}
ssh-keygen -t ecdsa -b 521
ssh-copy-id -i ~/.ssh/id_ecdsa.pub user@server.tld{% endhighlight %}

<p><i>Featured image by <a href="http://www.flickr.com/photos/koen_photos/">Koen Photos</a> under a CC-BY-ND license.</i></p>





