---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Moving from Ubuntu to Fedora
wordpress_id: 1105
wordpress_url: https://www.martineve.com/?p=1105
date: !binary |-
  MjAxMS0wNS0zMCAxMToxMzo1OCArMDIwMA==
date_gmt: !binary |-
  MjAxMS0wNS0zMCAxMToxMzo1OCArMDIwMA==
categories:
- Technology
- Linux
tags:
- Linux
- Ubuntu
- Fedora
comments:
- id: 6306
  author: Don Rideaux-Crenshaw
  author_email: dgcrow@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wNS0zMCAxMTo0NzoyNyArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNS0zMCAxMTo0NzoyNyArMDIwMA==
  content: If you can live without Gnome 3 try the xfce spin. It's much more forgiving
    of graphics card issues and has great performance even on old iron.
- id: 6307
  author: bodhi.zazen
  author_email: bodhi.zazen@ubuntu.com
  author_url: http://bodhizazen.net
  date: !binary |-
    MjAxMS0wNS0zMCAxNTowNDo1NSArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNS0zMCAxNTowNDo1NSArMDIwMA==
  content: ! '@ Martin - Aye, it is a transition and part of the problem with both
    Ubuntu and Fedora is that unity and gnome 3 are both new, and thus there may be
    bugs.
    As suggested by Don, it may help to try an alternate window manager, although
    that will not solve your nvidia problem (see below).
    @ Don: The problem is not gnome 3, the problem is with the nouveau drivers and
    one has the same problem on the XFCE, KDE, and LXDE spins.
    A potential solution is to install in low graphics mode and then install the nvidia
    driver.'
- id: 6311
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wNS0zMSAxMjo1OToxNSArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNS0zMSAxMjo1OToxNSArMDIwMA==
  content: ! "@Bodhi Thanks; yeah, I'm going to try the low graphics mode install.
    Is that only available from pure installation media, or can I get to it from the
    live CD/USB?\r\n\r\nThe only query I have, as to whether it's GNOME 3 or not,
    is that, in classic mode, it works fine. The problem only manifests when using
    GNOME shell. Very odd."
- id: 6313
  author: Steven Drinnan
  author_email: stevenjd12@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wNi0xNCAwMzozMToyNSArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNi0xNCAwMzozMToyNSArMDIwMA==
  content: ! "Looks like it's an issue with openGL. Maybe a new technology that has
    not been implemented in the prop driver. But can be fixed in the opensource version.
    \r\n\r\nSo I too have the problem, use open source drivers and not be able to
    play some 3D games (even the opensource ones) and shorter battery life on my netbook
    or install the Prop drivers and not use Gnome3 pretty bad really. :("
- id: 6315
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wNi0xNCAxMzo1MDo1MCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNi0xNCAxMzo1MDo1MCArMDIwMA==
  content: I actually got it working in the end. I installed using the low-graphics
    install, booted up and went through the akmod process for install prop driver,
    then removed the nouveau module, rebuilt initramfs and it's all working very well
    indeed, now!
doi: "https://doi.org/10.59348/5jgze-4t093"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/05/30/moving-from-ubuntu-to-fedora"
---
<p>A the time that I started writing this blog post, I was intending to extol the virtues of the newly released <a href="http://fedoraproject.org/">Fedora 15</a> compared to the trainwreck that is <a href="http://www.ubuntu.com/">Ubuntu 11.04</a>. It turns out the story isn't as clear cut as that, but wanted to give my experience in comparison installing across two machines.</p>
<p><img src="https://www.martineve.com/wp-content/uploads/2011/05/FEdora.jpg" alt="Fedora 15" title="Fedora 15" style="width:750px" class="alignnone size-full wp-image-1131" /></p>
<p>This all started when I upgraded my laptop (a Toshiba Satellite 650C) to Ubuntu 11.04 during the beta period earlier this year. I raised the issue that, with the fglrx driver installed, the system became unbearably slow. This was most apparent when using the Unity desktop, but even when reverting to classic GNOME I also experienced the same problem. I reported these bugs well within the beta cycle.</p>
<p>To my (and the many others who <a href="http://www.google.co.uk/search?source=ig&hl=en&rlz=&q=unity+slow&aq=f&aqi=g10&aql=&oq=">seemingly agree</a>) intense frustration, this was not fixed before launch. I felt that the six month schedule with no possibility for rethink was too short a window and that the developers really didn't care what they inflicted on users, even when they had reported issues within the beta window. I decided it was time to try a different distro.</p>
<p>I downloaded Fedora 15 beta, curious to see how the new GNOME 3 interface would feel. It was no exaggeration to say that Fedora 15 running off a live USB stick was <i>far quicker</i> than my Ubuntu 11.04 installation. It only took me half a day of trying it from a stick to realise that I wanted to switch, and so I did, painlessly and in one fell swoop. It took me a mere six hours to fully reinstall, get all my apps and data back on and up and running. Fedora even supports the encrypted boot process that I had greatly enjoyed in Ubuntu.</p>
<p>I've been using it for several weeks now and I'm mightily impressed. I really like GNOME 3 and it's so much snappier than Ubuntu 11.04. In my enthusiasm, I decided that I would get a dual-boot with Ubuntu going on my desktop with Fedora to try it there. This is where the qualification of my enthusiasm begins. I got through the installer fine (with a lot of GRUB problems that are specific to my hardware that most won't experience), but then had to install the Nvidia proprietary drivers. Normally I would have been more than happy with the nouveau open source alternative, but on my GeForce 9800 GT the nouveau drivers won't silence the fan, leading to a system that sounds like an aircraft launching. I was unable to get GNOME 3 working, stably, with the proprietary drivers. I installed them, but the screen would refuse to refresh and the entire thing was unusable. I intend to try again following <a href="http://blog.bodhizazen.net/linux/how-to-install-the-nvidia-driver-on-fedora-15/">some different instructions</a>, but this really needs to be fixed before I will be able to consider Fedora 15 a viable alternative for my main desktop.</p>
<p>The long and the short: if you have an ATI card, or an Nvidia card with which the nouveau driver works fine, Fedora 15 could well be for you. Try it out, though, because if, as in my case, you have trouble with the graphics driver and GNOME 3, you could be in for a nasty shock.</p>
<p><i>Screenshot by <a href="http://www.flickr.com/photos/naudinsylvain/">Sylvain Naudin</a> under a CC-BY-SA license.</i></p>





