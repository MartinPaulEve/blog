---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: OCZ RevoDrive on Abit Fatal1ty FP-IN9 SLI
wordpress_id: 610
wordpress_url: http://www.martineve.com/?p=610
date: !binary |-
  MjAxMS0wMS0yMSAwOTozMTowNiArMDEwMA==
date_gmt: !binary |-
  MjAxMS0wMS0yMSAwOTozMTowNiArMDEwMA==
categories:
- Technology
- Linux
tags:
- OCZ
- Revodrive
- Abit
- SSD
- PCI-E
- Bootloader
comments: []
doi: "https://doi.org/10.59348/h42mj-02016"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/01/21/ocz-revodrive-on-abit-fatal1ty-fp-in9-sli"
---
<div><a href="http://www.martineve.com/2011/01/21/ocz-revodrive-on-abit-fatal1ty-fp-in9-sli/xqkh/" rel="attachment wp-att-611"><img src="http://www.martineve.com/wp-content/uploads/2011/01/xqkh-e1295601585597-300x179.jpg" alt="My PC with open case" title="My PC" width="300" height="179" class="alignnone size-medium wp-image-611" /></a></div>
<div style="margin-top:10px">
<p>My Christmas present (I am SUCH a geek) was a lovely OCZ RevoDrive PCI-E SSD, with blistering 540mb/s read/write speeds. Very nice. However, it was not a simple install on my rig and I thought I'd share my basic tips from the experience. If you need the manual, it's on the official Abit site and there's lots of additional info at <a href="http://www.digital-daily.com/motherboard/abit_fp_in9_sli/print">Digital Daily</a>.</p>
</div>
<p><b>Flip the SLI chip.</b> I was convinced that the second PCI-E slot on my motherboard, an Abit Fatal1ty FP-IN9 SLI, was fried. No response at all. Well, not true actually, the board would power up, but nothing showed up at any stage of BIOS, POST, or in the Operating System.</p>
<p><b>Pull the power.</b> It's not enough to just flip the off switch on the back. If you are *sure* everything on the board is plugged in correctly, reset the CMOS (move CMOS jumper to pins 2+3, power on, power off, move jumper back to pins 1+2), then pull the mains completely. Leave it overnight if needs be, just make 100% sure it's gone through an entire power cycle. I have no idea why this works, clearing the CMOS should do it, but this was the only way I got the thing to be detected.</p>
<p><b>Install your bootloader to a real hard disk.</b> The Abit Fatal1ty FP-IN9 SLI doesn't support a bootloader on a PCI-E add-in card. I'm using Ubuntu, so I put grub onto one of my HDDs, but put the OS itself on the SSD.</p>
<p><b>On any hardware change, you will likely lose the RevoDrive.</b> If you install a new PCI card, expect there to be a chance that the RevoDrive will drop out of being detected. I found the CMOS clear cycle and power-pull combo to the only remedy.</p>
<p>Hope this helps someone.</p>





