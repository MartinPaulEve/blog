---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2008/12/07/bypassing-firewalls-using-ssh-reverse-forwarding
categories:
- Information Security
comments: []
date: 2008-12-07 04:34:48 +0100
date_gmt: 2008-12-07 04:34:48 +0100
doi: https://doi.org/10.59348/8e1wk-2wf36
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
title: Bypassing firewalls using SSH Reverse Forwarding
wordpress_id: 241
wordpress_url: http://pro.grammatic.org/post-bypassing-firewalls-using-ssh-reverse-forwarding-61.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmmqx3z2o"
---

<p>Sometimes you will find yourself on a machine that has no inbound connections allowed, which can make even the most basic task a complete pain. Never fear, if you can initiate an outbound connection to an SSH server of your choosing, it is no problem whatsoever to remap the ports by what is known as Reverse Forwarding.</p>
<p>The first step is to set up <a href="http://www.martineve.com/2008/12/07/ssh-key-based-password-less-login/">key-based, passwordless authentication in SSH</a>.</p>
<p>Secondly, we need to do a little bit of configuration to the SSH server, so become root:</p>

{% highlight bash %}
su -
{% endhighlight %}

<p>Then, edit /etc/ssh/sshd_config to include the line:</p>
<blockquote><p>GatewayPorts yes</p></blockquote>
<p>This enables reverse forwarding to listen on hosts other than localhost.</p>
<p>Next up, if your client is Windows you can add Tunnels under SSH -> Tunnels in PuTTY. A "remote" tunnel means that any connection coming in to the server will be forwarded to your client. A "dynamic" tunnel means that a SOCKS5 server will be setup locally on the client on the port you specify, allowing you to have an encrypted browsing session; very usefful for wireless hotspots.</p>
<p>The equivalent for Nix is:</p>

{% highlight bash %}
ssh -R [host:]serverport:localhost:port -l server_user_name server.address
{% endhighlight %}

<p>or for dynamic:</p>

{% highlight bash %}
ssh -D port -l server_user_name server_address
{% endhighlight %}

<p>Note that "localhost" in the above example will map to the client. So while it is possible to map to any server, localhost refers to the place where your client machine is: you will usually want to use localhost.</p>
<p>So now, any connection that comes to the mapped port on the server will be channeled down the SSH connection and the client software (PuTTY or SSH) will make a connection from the client, to the client, inside the firewall. Tada, firewall bypassed!</p>