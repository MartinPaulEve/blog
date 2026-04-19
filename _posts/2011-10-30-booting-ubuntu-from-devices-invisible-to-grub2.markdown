---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Booting Ubuntu from devices invisible to GRUB2
wordpress_id: 1572
wordpress_url: https://www.martineve.com/2011/10/30/booting-ubuntu-from-devices-invisible-to-grub2/
date: !binary |-
  MjAxMS0xMC0zMCAxODoxMjo0MiArMDEwMA==
date_gmt: !binary |-
  MjAxMS0xMC0zMCAxODoxMjo0MiArMDEwMA==
categories:
- Technology
- Linux
tags:
- Linux
- GRUB
comments: []
doi: "https://doi.org/10.59348/n3gpw-da192"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/10/30/booting-ubuntu-from-devices-invisible-to-grub2"
---
<p>...slightly misleading title; obviously, that doesn't work.</p>
<p>I have an OCZ RevoDrive SSD which, although very fast, has some serious problems with my BIOS. The consequence is that GRUB cannot see the device (well, it can, but only after a 15 minute de-power cycle), but Linux can. This causes some headaches.</p>
<p>The way I worked around this was to put /boot on a separate partition and have the root filesystem on the SSD. This was all well and good, except that Ubuntu's GRUB2 scripts generate an unbootable grub.cfg. This is owing to the fact that, even if it gets the hdd params right, it puts in a "search" line for a device that GRUB can't see, hence the fail. I'm going to assume that, if you understood the above, you're capable of using the grub recovery prompt to find your ubuntu installation and manually boot. When you're in, the way to fix this is fairly easy:</p>
<p>edit /usr/lib/grub/grub-mkconfig_lib</p>
<p>Comment out these lines:</p>

{% highlight bash %}
  if fs_uuid="`"${grub_probe}" --device "${device}" --target=fs_uuid 2> /dev/null`" ; then
    echo "search --no-floppy --fs-uuid --set=root ${fs_uuid}"
  fi
{% endhighlight %}

<p>Modify your /boot/device.map file to correctly identify your HDDs as per GRUB.</p>
<p>Run update-grub.</p>
<p><i>Featured image by <a href="http://www.flickr.com/photos/unavoidablegrain/">atduskgreg</a> under a CC-BY-NC-SA license.</i></p>





