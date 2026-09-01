---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2018/10/14/m-audio-trigger-finger-pro-synchronisation-problems
date: 2018-10-14
doi: https://doi.org/10.59348/31eg9-jtk52
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: M-Audio Trigger Finger Pro synchronisation problems
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m7iwqkw2o"
categories:
- Music
- Technology
---

If you read any review of the M-Audio Trigger Finger Pro, it sounds like a steal. A sequencer, drum machine, and more, all packed into a hardware unit that is available for about £100 on Ebay. Steal.

The problem is, it seems that these reviewers have never actually tried to record midi output from the device. The synchronisation is [totally messed up](http://community.m-audio.com/m-audio/topics/trigger-finger-pro-out-of-sync). The latency unpredictably varies between takes and the recorded output is never the same.

I was somewhat despairing at this, until I noticed that, in Bitwig, my DAW, playback _was_ in sync when I just used play. It was not in sync when I pressed record.

This appears to be something to do with the poor way that the Trigger Finger Pro handles MIDI start vs. continue messages.

In any case, I found a solution (that works in Bitwig, while I can't vouch for elsewhere). Simply start playback before pressing record on whatever lane you have hooked up to the Trigger Finger. Tada. Back in sync.