---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/07/22/using-elliptical-curve-cryptography-in-openssh
categories:
- Information Security
- Linux
comments:
- author: Efendi
  author_email: efendi@informatika.lipi.go.id
  author_url: ''
  content: I used Fedora 15 to create ecdsa as like as your inctructions, but that
    still cannot created ecdsa key pair.. What I have suppose to do?, Please help
    me and thank!
  date: 2011-08-03 07:38:00 +0200
  date_gmt: 2011-08-03 07:38:00 +0200
  id: 6514
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  content: Did you install OpenSSL from source as instructed? Paste the output of
    your OpenSSH ./configure.
  date: 2011-08-03 07:42:00 +0200
  date_gmt: 2011-08-03 07:42:00 +0200
  id: 6515
- author: Efendi
  author_email: efendi@informatika.lipi.go.id
  author_url: ''
  content: 'Not yet It was, but after I do reinstalling OpenSSL with source that U
    recommended. I got this statement when I had compiled command ./configure from
    OpenSSH : [root@XXXXXX openssh-5.8p2]# ./configure --with-selinux --bindir=/usr/bin
    --sbindir=/usr/sbin --with-ssl-dir=/usr/local/ssl/ checking for gcc... gcc checking
    for C compiler default output file name... a.out checking whether the C compiler
    works... yes checking whether we are cross compiling... no ... checking zlib.h
    presence... no checking for zlib.h... no configure: error: *** zlib.h missing
    - please install first or check config.log *** [root@XXXXXX openssh-5.8p2]# What
    should I do now? thank 4 Ur help! '
  date: 2011-08-04 08:06:00 +0200
  date_gmt: 2011-08-04 08:06:00 +0200
  id: 6518
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  content: "You need to install the packages that provide zlib.h.\n\nTry (as root):\n\nyum
    groupinstall \"Development Tools\"\n\nand\n\nyum install kernel-devel.x86_64\n
    (if running on 64 bit -- otherwise not entirely sure of package name)"
  date: 2011-08-04 08:19:00 +0200
  date_gmt: 2011-08-04 08:19:00 +0200
  id: 6519
- author: Efendi
  author_email: efendi@informatika.lipi.go.id
  author_url: ''
  content: 'I''m already solve for zlib problem but in ./configure i got "checking
    for selinux/selinux.h... no configure: error: SELinux support requires selinux.h
    header"... Do you have opinion, sir?'
  date: 2011-08-04 08:52:00 +0200
  date_gmt: 2011-08-04 08:52:00 +0200
  id: 6520
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  content: 'Try: yum install libselinux-devel'
  date: 2011-08-04 09:26:00 +0200
  date_gmt: 2011-08-04 09:26:00 +0200
  id: 6521
- author: Efendi
  author_email: efendi@informatika.lipi.go.id
  author_url: ''
  content: Thank a lot for your help. At now i can continue my works.
  date: 2011-08-05 02:08:00 +0200
  date_gmt: 2011-08-05 02:08:00 +0200
  id: 6523
date: 2011-07-22 15:49:15 +0200
last_modified_at: 2026-09-06
date_gmt: 2011-07-22 15:49:15 +0200
doi: https://doi.org/10.59348/dz3dw-gxh20
roguescholar: https://rogue-scholar.org/records/t8f5h-1x464
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mk4rvey2f
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- information security
- ssh
- cryptography
- security
title: Using Elliptical Curve Cryptography in OpenSSH
wordpress_id: 1329
wordpress_url: https://www.martineve.com/?p=1329
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mk4rvey2f"
kcworks: https://works.hcommons.org/records/hktfr-sjg51
references:
- title: Good practices for using ssh
  type: WebPage
  url: http://lackof.org/taggart/hacking/ssh/
- title: Downloads
  type: WebPage
  url: http://www.openssl.org/source/
  isPartOf:
    name: OpenSSL
    type: WebSite
- author: Koen
  title: Koen
  type: WebSite
  url: http://www.flickr.com/photos/koen_photos/
  isPartOf:
    name: Flickr
    type: WebSite
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