---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/03/02/sshsplit-a-dynamic-tunnel-multiplexer
categories:
- Programming
- Information Security
comments: []
date: 2010-03-02 13:11:34 +0100
last_modified_at: 2026-09-06
date_gmt: 2010-03-02 13:11:34 +0100
doi: https://doi.org/10.59348/gyg56-x5665
roguescholar: https://rogue-scholar.org/records/1a5yx-dta27
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmdxqw22a
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- sshsplit
- privacy
- ssh
- software
title: 'sshsplit: a dynamic tunnel multiplexer'
wordpress_id: 228
wordpress_url: http://pro.grammatic.org/post-sshsplit-a-dynamic-tunnel-multiplexer-74.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmdxqw22a"
kcworks: https://works.hcommons.org/records/s0q9m-7ym39
references:
- http://pro.grammatic.org/sshsplit/sshsplit-screen1.png # sshsplit screenshot 1 on pro.grammatic.org
- title: sshsplit
  type: SoftwareSourceCode
  url: https://launchpad.net/sshsplit
  isPartOf:
    name: Launchpad
    type: WebSite
---

<p>Introducing sshsplit</p>
<p>sshsplit is a GPL-3 licensed application that multiplexes ssh dynamic tunnels.</p>
<p><a href="http://pro.grammatic.org/sshsplit/sshsplit-screen1.png"><img style="width:500px;border:0px;" src="http://pro.grammatic.org/sshsplit/sshsplit-screen1.png" alt="sshsplit GUI"></img></a></p>
<p>For example, you might normally run:</p>
<blockquote><p>ssh -D 54321 remote-host</p></blockquote>
<p>to get a tunnel on 127.0.0.1:54321 that goes through remote-host.</p>
<p>However, if you are using a network-resource-intensive application (torrent clients for example), this single tunnel will not suffice for, say, 1000 concurrent connections.</p>
<p>sshsplit launches several instances of the ssh dynamic tunnel and then load balances between them.</p>
<p>If no arguments are passed, sshsplit launches the configuration GUI. Otherwise, for help, run: sshsplit -h</p>
<p>sshsplit can also be configured to use any binary you would like and you can suppress the default arguments it passes (-ND
<port>) using the -S option.</p>
<p><a href="http://www.martineve.com/sshsplit/sshsplit-screen2.png"><img style="width:500px;border:0px;" src="http://www.martineve.com/sshsplit/sshsplit-screen2.png" alt="sshsplit command line"></img></a></p>
<p>The code, my first effort in python, is available at <a href="https://launchpad.net/sshsplit">the sshsplit launchpad home</a>.</p>
<p>There is also a ppa that you can use to install sshsplit on Ubuntu machines on <a href="https://launchpad.net/~martineve/+archive/ppa">my launchpad page</a>.</p>
<p>Please report any bugs to launchpad!</p>