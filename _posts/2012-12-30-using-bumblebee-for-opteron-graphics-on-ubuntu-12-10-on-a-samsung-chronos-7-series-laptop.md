---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2012/12/30/using-bumblebee-for-opteron-graphics-on-ubuntu-12-10-on-a-samsung-chronos-7-series-laptop
categories:
- Linux
comments: []
date: 2012-12-30 13:20:41 +0100
date_gmt: 2012-12-30 13:20:41 +0100
doi: https://doi.org/10.59348/ybq3g-wh890
roguescholar: https://rogue-scholar.org/records/36mfr-m8t58
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mh7ece32h
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Linu
title: Using bumblebee for opteron graphics on Ubuntu 12.10 on a Samsung Chronos 7
  Series laptop
wordpress_id: 2563
wordpress_url: https://www.martineve.com/?p=2563
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mh7ece32h"
kcworks: https://works.hcommons.org/records/3rae7-5sb02
---

<p>Getting this to work has been the bane of my morning, so here's what I did to eventually get it working:</p>

{% highlight bash %}
sudo add-apt-repository ppa:bumblebee/stable
sudo add-apt-repository ppa:ubuntu-x-swat/x-updates
sudo apt-get update
sudo apt-get install bumblebee bumblebee-nvidia linux-headers-generic
sudo apt-get install linux-headers-$(uname -r)
sudo apt-get install nvidia-current
{% endhighlight %}

<p>Edit /etc/bumblebee/bumblebee.conf (as root). <a href="http://ubuntuforums.org/showthread.php?t=2043971">Change</a>:</p>
<blockquote><p>
Driver=<br />
to<br />
Driver=nvidia</p>
<p>and</p>
<p>KernelDriver=nvidia-current<br />
to<br />
KernelDriver=nvidia
</p></blockquote>
<p>Edit /etc/bumblebee/xorg.conf.nvidia (as root). <a href="https://github.com/Bumblebee-Project/Bumblebee/wiki/Troubleshooting">Change</a>:</p>
<p>Option "ConnectedMonitor" "DFP"</p>
<p>to</p>
<p>Option "ConnectedMonitor" "CRT"</p>
<p>A reboot now should enable you to do: "optirun glxgears" without any problems. If it isn't working, make sure that bumblebee-nvidia is actually installed. Also, when the nvidia-current package was installed, make sure it can find the kernel source and isn't giving an error showing that it didn't actually build the module.</p>
<p>My next step is to verify that bbswitch is actually working to give the power saving.</p>