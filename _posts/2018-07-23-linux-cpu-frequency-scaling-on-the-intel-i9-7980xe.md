---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2018/07/23/linux-cpu-frequency-scaling-on-the-intel-i9-7980xe
date: 2018-07-23
doi: https://doi.org/10.59348/sxzd8-ymd56
image:
  feature: geek.png
layout: post
ogImage: geek.png
title: Linux CPU Frequency Scaling on the Intel i9 7980XE
---

I spent some time this morning trying to work out why my CPU - the beastly Intel i9 7980XE - was capped at 2.6ghz when the BIOS allows scaling to 4.3ghz.

When I ran the usually suggested cpufreq and cpupower commands, I received: "no or unknown cpufreq driver is active on this CPU".

The reason for this was that you need, in the UEFI/BIOS, to enable: Intel Enhanced SpeedStep and the option to expose pstates. Once these are enabled, the CPU scales within linux and cpufreq commands work.