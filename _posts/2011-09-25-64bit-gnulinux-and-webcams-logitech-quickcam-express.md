---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/09/25/64bit-gnulinux-and-webcams-logitech-quickcam-express
categories:
- Linux
comments: []
date: 2011-09-25 07:28:09 +0200
date_gmt: 2011-09-25 07:28:09 +0200
doi: https://doi.org/10.59348/qd751-9gv90
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Linux
title: 64bit GNU/Linux and Webcams (Logitech Quickcam Express)
wordpress_id: 1505
wordpress_url: https://www.martineve.com/2011/09/25/64bit-gnulinux-and-webcams-logitech-quickcam-express/
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mjvjrh42h"
---

<p>I've just been playing around with my webcam, which I haven't hooked up in ages, and was unable to get it working under my 64bit Fedora installation. Having done a bit of reading, and having found that some applications can use the camera, I worked out the solution.</p>
<p><b>32bit applications need to have the 32bit library put into their LD_PRELOAD environment variable.</b></p>
<p>This will work only if your camera is being correctly detected, but doesn't seem to work in certain apps. To check, run dmesg and look for the following output:</p>

{% highlight bash %}
[    2.878055] usb 2-4: New USB device found, idVendor=046d, idProduct=0928
[    2.878261] usb 2-4: New USB device strings: Mfr=1, Product=2, SerialNumber=0
[    2.878458] usb 2-4: Product: Camera
[    2.878649] usb 2-4: Manufacturer:         
{% endhighlight %}

<p>I tried doing this via .bashrc originally, but the problem was that 64bit applications then continually churned out garbage. The eventual solution was as follows:</p>
<p>For each application that uses a 32bit component for which you want webcam access (Firefox/Flash, Skype) create a file called program-cam-fix in /usr/bin/.</p>
<p>Here's my firefox-cam-fix file:</p>

{% highlight bash %}
#! /bin/sh
LD_PRELOAD=/usr/lib/libv4l/v4l1compat.so firefox $1
{% endhighlight %}

<p>My skype-cam-fix file doesn't have the $1 at the end as the launcher doesn't pass any arguments.</p>
<p>Next, modify the files /usr/share/applications/mozilla-firefox.desktop and /usr/share/applications/skype.desktop so that the exec lines point to your new scripts (/usr/bin/skype-cam-fix or /usr/bin/firefox-cam-fix). You'll need to use sudo.</p>
<p>Now, when you start skype, or firefox, you should be able to use the webcam.</p>