---
archive: https://wayback.archive-it.org/22123/20241101171236/https://eve.gd/2026/03/25/how-to-get-a-blocked-usb-stack-and-dead-microphone-working-again-on-linux
date: 2026-03-25
doi: https://doi.org/10.59348/bn9z8-ehk76
image:
  credit: israel palacio on unsplash
  creditlink: https://unsplash.com/@othentikisra
  feature: mic.jpg
  title: An image of a microphone
layout: post
ogImage: images/mic.jpg
title: How to get a blocked USB stack and dead microphone working again on Linux
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7luwxapm2a"
---

I have been having an intermittent problem where my microphone just drops out arbitrarily on Linux and I can't access it anymore. It turns out that this was actually due to a dodgy USB hub inside the motherboard of my computer. 

<img src="/images/mic.jpg" alt="An image of a microphone" style="width: 100%;"/>

I was finding that looking at /sys/bus/usb/devices/1-5.1/power/runtime_status (this will be different on your machine) was showing "error". Oh dear, said Paddington. The symptom was that the device wasn't visible as an audio microphone input. I couldn't use the microphone, and lots of USB devices were all over the place. For a short while the microphone would appear in the volume control list, but I could not get any signal through it.

The solution in the end was actually quite simple, I just needed to reset the USB "hub". For me, this is what worked:

	sudo bash -c 'usbreset 001/003; sleep 2; usbreset 001/002'
	systemctl --user restart wireplumber pipewire pipewire-pulse

Not a very exciting post I know, but someone might be helped by it.