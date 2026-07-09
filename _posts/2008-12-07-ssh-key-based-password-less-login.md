---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2008/12/07/ssh-key-based-password-less-login
categories:
- Technology
- InfoSec
- Linux
comments:
- author: Bypassing firewalls using SSH Reverse Forwarding | Martin Paul Eve
  author_email: ''
  author_url: http://www.martineve.com/2008/12/07/bypassing-firewalls-using-ssh-reverse-forwarding/
  content: '[...] cand. at the University of Sussex    Skip to content HomeAboutCurriculum
    VitaeProfile              &larr; SSH Key Based, Password Less Login Fetching files
    via echo, FTP in a non interactive shell environment [...]'
  date: 2010-11-07 12:10:19 +0100
  date_gmt: 2010-11-07 12:10:19 +0100
  id: 182
date: 2008-12-07 04:11:13 +0100
date_gmt: 2008-12-07 04:11:13 +0100
doi: https://doi.org/10.59348/4s7eb-h5240
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- privacy
- ssh
- Linux
- passworless login
title: SSH Key Based, Password Less Login
wordpress_id: 242
wordpress_url: http://pro.grammatic.org/post-ssh-key-based-password-less-login-60.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmnb4ly2r"
---

<p>It can be very handy to be able to login to an SSH shell without supplying a password. Here's how.</p>
<p>Firstly, on your client machine, generate a keypair. If you are using Windows you can do this using PuTTYgen. If you are on a Nix machine issue:</p>

{% highlight bash %}
ssh-keygen -t dsa
{% endhighlight %}

<p>Next up, we need to copy the public key to the server. If you are on Linux you can use scp to do this:</p>

{% highlight bash %}

cd .ssh/
scp id_dsa.pub server_user_name@server.address:./id_dsa.pub

{% endhighlight %}

<p>If you are on Windows you could use sftp or similar to transfer the key across. You should end up with a file called id_dsa.pub in your home directory on the server.</p>
<p>Now, on the server, with your regular user account:</p>

{% highlight bash %}

cd .ssh
touch authorized_keys2
chmod 600 authorized_keys2
cat ../id_dsa.pub >> authorized_keys2
rm ../id_dsa.pub

{% endhighlight %}

<p>Now, on Windows fire up a PuTTY session specifying the private key under SSH -> Auth. On Nix, simply give:</p>

{% highlight bash %}

ssh -l server_user_name server.address

{% endhighlight %}

<p>With any luck, you will be sorted for password-less login!</p>