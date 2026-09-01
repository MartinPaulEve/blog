---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2021/04/13/moog-minitaur-the-editor-and-exclusive-usb-lock
date: 2021-04-13
doi: https://doi.org/10.59348/ghsyh-2gc97
image:
  feature: header_moog.png
layout: post
ogImage: images/header_moog.png
title: 'Moog Minitaur: the editor and exclusive USB lock'
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m3hbque2q"
categories:
- Music
- Technology
---

I love my Moog Minitaur synth. It's a great little bass station that packs a punch. However, I have been facing some issues using its full functionality.

Namely, there's a software plugin that enables you to tweak all the settings from the DAW. It controls the synth over midi via USB. This is all well and good, but I found that, when I enabled this, I could no longer send midi note data from my DAW (Bitwig).

The solution that I came up with was somewhat hacky, but it works. I use the USB connection to control the synths parameters via the plugin and use a midi cable from my audio interface to send midi note data/play the synth. So that then yields two midi IN channels that do not overlap with one another.