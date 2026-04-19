---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: ! 'Open Hardware: the Netgear WNR3500L'
wordpress_id: 791
wordpress_url: https://www.martineve.com/?p=791
date: !binary |-
  MjAxMS0wMi0xOCAwOTo1OTozMiArMDEwMA==
date_gmt: !binary |-
  MjAxMS0wMi0xOCAwOTo1OTozMiArMDEwMA==
categories:
- Technology
- Open Access
- Linux
tags: []
comments:
- id: 6546
  author: otter9099
  author_email: mattbeardall@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0xMC0xNiAwNDo0MjowMCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0xMC0xNiAwNDo0MjowMCArMDIwMA==
  content: Have you been able to get your router setup as your pxe server yet? Can
    you do a write up on it?
- id: 6550
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  date: !binary |-
    MjAxMS0xMC0xNiAyMDowODowMCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0xMC0xNiAyMDowODowMCArMDIwMA==
  content: ! 'Hi, I did manage to get a PXE server working, but the result was hugely
    unstable. Obviously, it''s wired-only (no PXE WLAN boot) and I managed to get
    a Ubuntu/GNOME environment up and running, but at that point (after about 20 seconds)
    the system started to crash out. I didn''t debug it any further as I wanted to
    pursue projects I might actually use!
    If you wanted to replicate, you need to install Optware: http://tomatousb.org/tut:optware-installation
    Then setup a TFTP server and configure your DHCP server (on tomato: Advanced -&gt;
    DHCP) with dhcp-boot=pxelinux.0,router2,192.168.0.50
    In this case (as you can see) I was using my second router to serve the files,
    but you could just as easily set your primary router (and IP address appropriately)
    to serve.
    I was serving the OS from an attached USB hard drive. I suppose that could, also,
    have been the point of fault...'
doi: "https://doi.org/10.59348/tt2fs-1hp39"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/02/18/open-hardware-the-netgear-wnr3500l"
---
<p><i>Featured image copyright, and courtesy of, <a href="http://www.myopenrouter.com">My Open Router</a>.</i></p>
<p>I've been, over the past few years, through about 3 different routers. I had a Thompson Speedtouch, a Netgear DG834GT and, most recently, a Netgear DGN2200. The problem I have always experienced, though, is that when I open a large number of connections (say, using BitTorrent), all these models die a miserable death. DHCP keels over so no new devices can get on the network and my connection crawls to a halt, sometimes veering between 1MiB/s down, then at 0KiB/s for five minutes plus.</p>
<p>Anyway, in a burst of anger at this situation, I did some research last week and came up with a solution that I thought would work; I bought myself a Netgear WNR3500L: billed as the first "open" router on the market. Now, by "open" it is meant that the end user has the ability to flash whatever software they want onto the device and Netgear has embedded a recovery mode into the device that can be accessed by USB serial so that, in case of emergency, the device can be "unbricked". This was, from my ideological perspective, ideal!</p>
<p>I spent a long time debating whether to get this device. It doesn't, after all, come with an ADSL2+ modem built-in. However, the solution was simple: I simply put one of my old devices into Bridge Mode (whereby the router acts purely as a modem and delegates all routing to the attached host, in this case the WNR3500L).</p>
<p>Once the device arrived, I flashed <a href="http://www.myopenrouter.com/article/25150/Toastman-s-Tomato-USB-Firmware-on-the-NETGEAR-WNR3500L/">ToastMan's build</a> of the "Tomato", USB, VPN-enabled firmware. This allows direct setup of an OpenVPN network on the router, as well as turning it into a USB NAS; simply plug in a hub and your USB devices and they can be shared over the network. My next task is to get a PXE server running off this environment so that I can install Ubuntu Alphas/Betas and have them boot over the network, directly from my router.</p>
<p>Overall, in the few days I've had it, this has proved an excellent device. I mention it here as a review for anybody interested (there are more comprehensive guides), but also because it is fantastic to see hardware moving in the right direction: towards openness.</p>





