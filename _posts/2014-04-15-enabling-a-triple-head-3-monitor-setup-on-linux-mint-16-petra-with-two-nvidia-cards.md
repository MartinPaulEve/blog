---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2014/04/15/enabling-a-triple-head-3-monitor-setup-on-linux-mint-16-petra-with-two-nvidia-cards
categories:
- Technology
- Linux
comments: []
date: 2014-04-15 08:26:11 +0200
date_gmt: 2014-04-15 07:26:11 +0200
doi: https://doi.org/10.59348/djfyg-jmn80
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Linux
title: Enabling a triple-head (3 monitor) setup on Linux Mint 16 ("Petra") with two
  Nvidia cards
wordpress_id: 3078
wordpress_url: https://www.martineve.com/?p=3078
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mfdktxx2t"
---

<p>OK, so this was utterly painful and I needed to share what finally worked for me. I have 2 x Nvidia GTX480 cards. I have 3 x monitors. I wanted to be able to run all three off the same box, using it as a single X Screen (i.e. so I can move windows between screens and it acts correctly). No matter what I tried, it wouldn't let me do so with the proprietary driver. I <a href="http://unix.stackexchange.com/questions/123862/how-can-i-get-xrandr-to-detect-both-nvidia-cards-2-x-gtx480-triple-head">asked on Stack Exchange</a> and got somewhere closer. Here's what worked:</p>
<div style="clear:both"/>
<ul>
<li>Use driver 319.60 or 337.12. 331.20 did <i>not</i> work for me.</li> <b>Update (28th August 2015): </b> I've now had success with driver 346, so this tutorial is still relevant.
<li>Install the SLI bridge (hardware). Even though you are not using SLI, you need to put the bridge in and enable it.</li>
<li>Use SLIMosaic and BaseMosaic options. <i>Ignore the fact the manual implies it won't work for this card. It does.</i></li>
</ul>
<p>My XConfig looks like this:</p>

{% highlight bash %}
Section "ServerLayout"
    Identifier     "Layout0"
    Screen      0  "Screen0"
EndSection

Section "Monitor"

    # HorizSync source: edid, VertRefresh source: edid
    Identifier     "Monitor1"
    VendorName     "Unknown"
    ModelName      "Ancor Communications Inc ASUS VS247"
    HorizSync       24.0 - 83.0
    VertRefresh     50.0 - 75.0
    Option         "DPMS"
EndSection

Section "Monitor"

    # HorizSync source: edid, VertRefresh source: edid
    Identifier     "Monitor0"
    VendorName     "Unknown"
    ModelName      "LG Electronics W2243"
    HorizSync       30.0 - 83.0
    VertRefresh     56.0 - 75.0
    Option         "DPMS"
EndSection

Section "Monitor"

    # HorizSync source: unknown, VertRefresh source: unknown
    Identifier     "Monitor2"
    VendorName     "Unknown"
    ModelName      "AOC LM720/LM720A"
    HorizSync       30.0 - 83.0
    VertRefresh     55.0 - 75.0
    Option         "DPMS"
EndSection

Section "Device"
    Identifier     "Device1"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    BoardName      "GeForce GTX 480"
    BusID          "PCI:1:0:0"
EndSection

Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    BoardName      "GeForce GTX 480"
    BusID          "PCI:1:0:0"
EndSection

Section "Screen"
    Identifier     "Screen0"
    Device         "Device0"
    Monitor        "Monitor0"		
    DefaultDepth    24
    Option         "Stereo" "0"
    Option         "MultiGPU" "Off"
    Option         "SLI" "on"
    Option         "SLIMosaic" "True"
    Option         "BaseMosaic" "True"
    Option         "MetaModes" "GPU-1.CRT-0: 1280x1024+0+0, GPU-0.CRT-0: 1920x1080+1280+0, GPU-0.DFP-2: 1920x1080+3200+0"
    SubSection     "Display"
        Depth       24
    EndSubSection
EndSection

{% endhighlight %}

<p>Totally weirdly, you don't need to have more than one device listed (my second card is at "PCI:1:0:0").</p>
<p>Note also that, despite this then yielding two providers, when it's working xrandr 1.4 (which supports multiple GPUs) only lists 1 provider:</p>

{% highlight bash %}
xrandr --listproviders
Providers: number : 1
Provider 0: id: 0x279 cap: 0x1, Source Output crtcs: 4 outputs: 10 associated providers: 0 name:NVIDIA-0"
{% endhighlight %}

<p>Anyway, it now works!</p>