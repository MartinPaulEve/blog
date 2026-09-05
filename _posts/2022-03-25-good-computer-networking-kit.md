---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2022/03/25/good-computer-networking-kit
date: 2022-03-25
doi: https://doi.org/10.59348/1993a-a0q31
roguescholar: https://rogue-scholar.org/records/ptdbe-q4q42
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lzcelg22a
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: Good computer networking kit
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lzcelg22a"
categories:
- Technology
kcworks: https://works.hcommons.org/records/12v3g-xq789
references:
- https://www.marvell.com/products/ethernet-adapters-and-controllers/fastlinq-edge-ethernet-controllers.html # Marvell FastLinQ edge Ethernet controllers product page
---

OK, this is different from my usual fare, but I've been thinking about upgrading my home LAN to 10GbE. My WAN connection is now more than 1Gbit and so I'm maxxing out the link. Finding kit that works on Linux (and even, shudder, FreeBSD), though, is somewhat tricky. Here's what I've found:

* QNAP QNA-T310G1T Thunderbolt 3 to 10GbE NBASE-T Adapter -- a Thunderbolt adapter that supports 10BASE-T.
* QNAP QXG-10G2TB 2-Port PCIe Network Interface Card (10GbE RJ45) -- a PCIe x8 adapter with two ports. Runs the Marvell AQtion AQC113C chipset. Apparently there _may_ be [FreeBSD support for this](https://www.marvell.com/products/ethernet-adapters-and-controllers/fastlinq-edge-ethernet-controllers.html).
* TP-Link TL-SX105 5-Port Unmanaged Desktop 10-Gigabit Switch -- one of the only unmanaged fanless 10GbE switches that I could find
* The Draytek Vigor3910 looks like an amazing router. It has multi-WAN, 2x SFP+ ports, 2x 2.5GbE, and 4x 1GbE ports. If it had 1x more 10GbE ports, it would be ideal
* The Netgate 6100 MAX is also a great-looking piece of kit. 2x 10GbE SFP+, 4x 2.5GbE RJ-45 ("unswitched"?) ports. Again, it's the lack of a third GbE port here that isn't great. You want 3x 10GbE ports so you can have 2x multi-gigabit WAN connections and then one LAN uplink port

There is also the QNA-T310G1S, which is a Thunderbolt connector for 10 gig SFP+ as opposed to 10BASE-T.