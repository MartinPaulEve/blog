---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Fixing headphone jack on Toshiba Satellite C650D under Ubuntu Linux Maverick
wordpress_id: 442
wordpress_url: http://www.martineve.com/?p=442
date: !binary |-
  MjAxMC0xMS0yNCAxMDoxNTo0OCArMDEwMA==
date_gmt: !binary |-
  MjAxMC0xMS0yNCAxMDoxNTo0OCArMDEwMA==
categories:
- Technology
- Linux
tags: []
comments:
- id: 2809
  author: dan
  author_email: conejitosuavecito@hotmail.com
  author_url: ''
  date: !binary |-
    MjAxMC0xMS0yNSAyMjoyMToxNyArMDEwMA==
  date_gmt: !binary |-
    MjAxMC0xMS0yNSAyMjoyMToxNyArMDEwMA==
  content: ! 'God man!, I LOVE YOU! Thank you so much. I really was thinking about
    giving up, from Mexico: THANKS.'
- id: 6176
  author: naitech
  author_email: mjthiga@yahoo.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMi0xMSAxMDoxMDowOCArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMi0xMSAxMDoxMDowOCArMDEwMA==
  content: Worked on my Toshiba C650. Thank you very much.
- id: 6257
  author: SANTIAGO
  author_email: santiago.s.fragoso@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0yOSAwNDoyODoyNiArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0yOSAwNDoyODoyNiArMDIwMA==
  content: ! "i have the same problem, ive tried to fix it but i dont realy know hot
    to add thet comand. i did enter to the modprobe.d directory, but afther that i
    dont know what to do. \n\nhelp me please!!"
- id: 6258
  author: Kevin
  author_email: hamishyhoo@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0yOSAyMDo1Mjo1MyArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0yOSAyMDo1Mjo1MyArMDIwMA==
  content: ! "Wow! This actually worked! \r\n\r\nToshiba Satellite L655D-S5050"
- id: 6259
  author: Kevin
  author_email: hamishyhoo@gmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0yOSAyMDo1ODoxOCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0yOSAyMDo1ODoxOCArMDIwMA==
  content: ! "In the modprobe.d directory, there should be a file named \"alsa-base.conf\".
    You need to add \"options snd-hda-intel model=ideapad\" to the file. I put it
    at the bottom of the file. You will need to open the file with root privileges,
    though, otherwise you will not be able to edit the file. I used this https://help.ubuntu.com/community/RootSudo
    to help me figure it out. \r\n\r\nHope I could help! :)"
- id: 6260
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0zMCAwODo1MTo0MSArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0zMCAwODo1MTo0MSArMDIwMA==
  content: Glad to have helped :)
- id: 6261
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0zMCAwODo1MzozOSArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0zMCAwODo1MzozOSArMDIwMA==
  content: ! "As Kevin says, you need to edit the file mentioned.\r\n\r\nEasiest way:\r\n\r\nOpen
    a terminal.\r\n\r\nType:\r\n\r\ngksu gedit /etc/modprobe.d/alsa-base.conf \r\n\r\nPress
    enter and it will ask for your password.\r\n\r\nIn gedit, add:\r\n\r\noptions
    snd-hda-intel model=ideapad\r\n\r\nto the bottom of the file and save it. Be very
    careful not to change anything else, this instance of gedit is running with superuser
    permissions and you could damage your installation.\r\n\r\nYou'll need to reboot
    for the changes to take effect."
- id: 6290
  author: Zane
  author_email: zane@Ellzey.org
  author_url: ''
  date: !binary |-
    MjAxMS0wNS0wNSAwNTozMTo1NiArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNS0wNSAwNTozMTo1NiArMDIwMA==
  content: Thank you so much!  I installed Linux Mint on a newly purchased Toshiba
    laptop this weekend.  I had the same symptoms, speakers worked but not the headphone
    jack.  I was afraid the sound card or board was defective.  Fortunately, your
    tip worked and now my headphones work properly.
- id: 6496
  author: Shahid Christopher
  author_email: shahid.christopher@yahoo.com
  author_url: ''
  date: !binary |-
    MjAxMS0wNy0wMiAwMTowMDowMCArMDIwMA==
  date_gmt: !binary |-
    MjAxMS0wNy0wMiAwMTowMDowMCArMDIwMA==
  content: thanks man!
doi: "https://doi.org/10.59348/jakqz-9mm63"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/11/24/fixing-headphone-jack-on-toshiba-satellite-c650d-under-ubuntu-linux-maverick"
---
<p>There is an annoying bug on Toshiba Satellite Machines running Ubuntu Linux (seems variants up to Maverick) which means that plugging in to the headphone jack does not work and, also, that speakers continue to play sound.</p>
<p>The solution, after much digging, is to add:</p>
<p><code>options snd-hda-intel model=ideapad</code></p>
<p>to /etc/modprobe.d/alsa-base.conf </p>
<p>I've put in a <a href="https://bugs.launchpad.net/ubuntu/+source/alsa-driver/+bug/680844">bug report</a>, so hopefully this can get a fix in Natty.</p>





