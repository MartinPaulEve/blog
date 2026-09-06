---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2020/12/12/how-to-install-ubuntu-on-the-hp-dragonfly-elite
date: 2020-12-12
last_modified_at: 2026-09-06
doi: https://doi.org/10.59348/bf1js-jhp50
roguescholar: https://rogue-scholar.org/records/rct2m-vr820
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m4pln3g2h
image:
  feature: header_laptop.png
layout: post
ogImage: images/header_laptop.png
title: 'How to install Ubuntu on the HP Dragonfly Elite (hint: disable Optane)'
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m4pln3g2h"
categories:
- Linux
kcworks: https://works.hcommons.org/records/hac12-f6317
references:
- author: Jim Salter
  date: '2020-01-27'
  title: 'Linux on laptops: Ubuntu 19.10 on the HP Dragonfly Elite G1'
  type: NewsArticle
  url: https://arstechnica.com/gadgets/2020/01/linux-on-laptops-ubuntu-19-10-on-the-hp-dragonfly-elite-g1/
  isPartOf:
    name: Ars Technica
    type: Periodical
- title: SATECHI 8-in-1 USB-C Hub V2
  type: WebPage
  url: https://www.amazon.co.uk/dp/B075FW7H5J
---

There's a prominent post at Ars Technica called [Linux on laptops: Ubuntu 19.10 on the HP Dragonfly Elite G1](https://arstechnica.com/gadgets/2020/01/linux-on-laptops-ubuntu-19-10-on-the-hp-dragonfly-elite-g1/) that implies that it is easy and straightforward to install Ubuntu on the HP Dragonfly Elite laptop. The post is correct that releases later than 19.10 have full kernel support for nearly all of the laptop's hardware, but there are some very important caveats to the install.

1. You can leave secure boot enabled, but pay attention to the Ars Technica post. When "Press any key to perform MOK management", you should enter that. As the Ars Technica post puts it: From here, you've got to select "Enroll MOK" from an equally bare-bones menu, offering that choice along with "Continue boot," "Enroll key from disk," and "Enroll hash from disk." This brings you to "View key 0" or "Continue," from which you should pick "Continue." Then it's "Yes" from no or yes, and finally you're presented with a "Password:" prompt, at which you type in the password you created when opting to configure Secure Boot back at the Ubuntu installer.

2. I would recommend _disabling fast boot_ and adding a 5 second delay to your boot sequence for ease of accessing BIOS etc.

3. OK, but there's a massive catch that nobody has mentioned anywhere. If you try this install with Intel Optane enabled, your install will die hard. Ubuntu will not come up as a menu option in the UEFI list. To fix this, you need to go into the BIOS and manage third-party ROM stuff (F3). Once you have disabled Intel Optane, you can proceed with the Ubuntu installation.

4. If you installed Ubuntu before disabling Optane you _should_ be able just to reinstall after doing so and you'll be up and running. If, like me, however, you had gone in and messed about with UEFI files in order to "fix" your install, you may have a totally unbootable laptop. Indeed, I actually had a situation where the laptop was unbootable and the recovery partition wouldn't launch either. Argh! The solution to this is both simple and quite a pain. I used a [Satechi USB-C adapter](https://www.amazon.co.uk/gp/product/B075FW7H5J/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1) to add an ethernet port to the laptop and then pressed F11 at boot. From there, I selected "Recover from Network". Remarkably, this worked! The laptop booted from HP's remote recovery image, over the internet, and totally restored itself. Admittedly, it _did_ mess one thing up: I no longer have Word and the bundled software. Also, the installer never "completed" -- it just say there eventually saying "We are recovering your PC" or whatever with all the boxes greyed out. After an hour, though, I just powered down, rebooted, and all was fine.

So, this is basically to say: the one thing that nobody told me for the install was _disable Optane_. I cannot stress this enough: _DISABLE OPTANE_. And your life will be so much easier. Hopefully point 4 above will help any unfortunate soul who ended up in the same boat as me.