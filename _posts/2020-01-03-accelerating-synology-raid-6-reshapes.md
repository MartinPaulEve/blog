---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2020/01/03/accelerating-synology-raid-6-reshapes
date: 2020-01-03
doi: https://doi.org/10.59348/r1n4g-g3187
roguescholar: https://rogue-scholar.org/records/2rc5p-8p982
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m6jxogi2h
layout: post
title: Accelerating Synology RAID 6 (SHR-2) reshapes
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m6jxogi2h"
categories:
- Linux
kcworks: https://works.hcommons.org/records/c71ng-7fa17
references:
- https://www.cyberciti.biz/tips/linux-raid-increase-resync-rebuild-speed.html # cyberciti.biz guide on Linux RAID resync speed
---

Urgh. I had a RAID 6 reshape on my NAS that was projected to take 28 days to complete, I kid you not. It was stuck at an abysmal 4MB/s transfer rate. Here's how to unblock it.

First, follow [all the advice on general raid speedups](https://www.cyberciti.biz/tips/linux-raid-increase-resync-rebuild-speed.html) -- assuming md2 is your RAID device and you need to replace sd[DEVICE] below with the correct block devices that constitute the array:

>  echo 50000 > /proc/sys/dev/raid/speed_limit_min

>  echo 100000 > /proc/sys/dev/raid/speed_limit_max

>  blockdev --setra 65536 /dev/md2

>  echo 32768 > /sys/block/md2/md/stripe_cache_size

>  echo 1 > /sys/block/sd[DEVICE]/device/queue_depth

This is all common advice that it is easy to find. But I was still stuck at the hideous transfer rate. I was worried there was a firmware fault with my drives. What unblocked it for me was:

> echo max > /sys/block/md2/md/sync_max

Bingo. Up to 45MB/s now, even during heavy write usage from other processes.