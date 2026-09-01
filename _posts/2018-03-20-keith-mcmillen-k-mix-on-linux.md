---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2018/03/20/keith-mcmillen-k-mix-on-linux
date: 2018-03-20
doi: https://doi.org/10.59348/6cekh-6be26
roguescholar: https://rogue-scholar.org/records/b6m9g-msw09
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m7ul7j62o
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: Keith McMillen K-Mix on Linux
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m7ul7j62o"
categories:
- Linux
- Music
---

I have a Keith McMillen K-Mix audio device that I use for music-making. I noticed, though, that if you have a simple stereo setup on this, with, say, monitors plugged into outputs 1 and 2 (the master outs) then you basically lose a huge amount of bass response on Linux. I confirmed this trying it on Windows and Linux and, in Linux, the bass is totally missing. In fact, the sound is weak.

The reason for this turns out to be that because it has eight outputs, Pulseaudio/alsa treat the device as a multichannel output. So the subwoofer is assigned to port 6 or so and all bass output is routed there. This is not what I want.

The solution turned out to be to create a virtual sink in Pulseaudio by adding this at the end of /etc/pulse/default.pa:

>load-module module-remap-sink remix=no sink_name=stereo-downmix master=alsa_output.usb-Keith_McMillen_Instruments_K-Mix-00.multichannel-output channels=10 master_channel_map=front-left,front-right,front-left,front-right,front-left,front-right,front-left,front-right,front-left,front-right channel_map=front-left,front-right,rear-left,rear-right,lfe,lfe,front-center,front-center,side-left,side-right

This creates a virtual device that downmixes the channels on the K-Mix to stereo.

In order for it to work, after adding that line, you need to run pulseaudio -k