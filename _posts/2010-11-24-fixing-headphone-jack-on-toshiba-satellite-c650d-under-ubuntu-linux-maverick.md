---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/11/24/fixing-headphone-jack-on-toshiba-satellite-c650d-under-ubuntu-linux-maverick
categories:
- Linux
comments:
- author: dan
  author_email: conejitosuavecito@hotmail.com
  author_url: ''
  content: 'God man!, I LOVE YOU! Thank you so much. I really was thinking about giving
    up, from Mexico: THANKS.'
  date: 2010-11-25 22:21:17 +0100
  date_gmt: 2010-11-25 22:21:17 +0100
  id: 2809
- author: naitech
  author_email: mjthiga@yahoo.com
  author_url: ''
  content: Worked on my Toshiba C650. Thank you very much.
  date: 2011-02-11 10:10:08 +0100
  date_gmt: 2011-02-11 10:10:08 +0100
  id: 6176
- author: SANTIAGO
  author_email: santiago.s.fragoso@gmail.com
  author_url: ''
  content: "i have the same problem, ive tried to fix it but i dont realy know hot
    to add thet comand. i did enter to the modprobe.d directory, but afther that i
    dont know what to do. \n\nhelp me please!!"
  date: 2011-03-29 04:28:26 +0200
  date_gmt: 2011-03-29 04:28:26 +0200
  id: 6257
- author: Kevin
  author_email: hamishyhoo@gmail.com
  author_url: ''
  content: "Wow! This actually worked! \r\n\r\nToshiba Satellite L655D-S5050"
  date: 2011-03-29 20:52:53 +0200
  date_gmt: 2011-03-29 20:52:53 +0200
  id: 6258
- author: Kevin
  author_email: hamishyhoo@gmail.com
  author_url: ''
  content: "In the modprobe.d directory, there should be a file named \"alsa-base.conf\".
    You need to add \"options snd-hda-intel model=ideapad\" to the file. I put it
    at the bottom of the file. You will need to open the file with root privileges,
    though, otherwise you will not be able to edit the file. I used this https://help.ubuntu.com/community/RootSudo
    to help me figure it out. \r\n\r\nHope I could help! :)"
  date: 2011-03-29 20:58:18 +0200
  date_gmt: 2011-03-29 20:58:18 +0200
  id: 6259
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  content: Glad to have helped :)
  date: 2011-03-30 08:51:41 +0200
  date_gmt: 2011-03-30 08:51:41 +0200
  id: 6260
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  content: "As Kevin says, you need to edit the file mentioned.\r\n\r\nEasiest way:\r\n\r\nOpen
    a terminal.\r\n\r\nType:\r\n\r\ngksu gedit /etc/modprobe.d/alsa-base.conf \r\n\r\nPress
    enter and it will ask for your password.\r\n\r\nIn gedit, add:\r\n\r\noptions
    snd-hda-intel model=ideapad\r\n\r\nto the bottom of the file and save it. Be very
    careful not to change anything else, this instance of gedit is running with superuser
    permissions and you could damage your installation.\r\n\r\nYou'll need to reboot
    for the changes to take effect."
  date: 2011-03-30 08:53:39 +0200
  date_gmt: 2011-03-30 08:53:39 +0200
  id: 6261
- author: Zane
  author_email: zane@Ellzey.org
  author_url: ''
  content: Thank you so much!  I installed Linux Mint on a newly purchased Toshiba
    laptop this weekend.  I had the same symptoms, speakers worked but not the headphone
    jack.  I was afraid the sound card or board was defective.  Fortunately, your
    tip worked and now my headphones work properly.
  date: 2011-05-05 05:31:56 +0200
  date_gmt: 2011-05-05 05:31:56 +0200
  id: 6290
- author: Shahid Christopher
  author_email: shahid.christopher@yahoo.com
  author_url: ''
  content: thanks man!
  date: 2011-07-02 01:00:00 +0200
  date_gmt: 2011-07-02 01:00:00 +0200
  id: 6496
date: 2010-11-24 10:15:48 +0100
date_gmt: 2010-11-24 10:15:48 +0100
doi: https://doi.org/10.59348/jakqz-9mm63
roguescholar: https://rogue-scholar.org/records/jz9s9-p5g23
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mllb36j2q
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags: []
title: Fixing headphone jack on Toshiba Satellite C650D under Ubuntu Linux Maverick
wordpress_id: 442
wordpress_url: http://www.martineve.com/?p=442
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mllb36j2q"
kcworks: https://works.hcommons.org/records/4y941-c4w25
---

<p>There is an annoying bug on Toshiba Satellite Machines running Ubuntu Linux (seems variants up to Maverick) which means that plugging in to the headphone jack does not work and, also, that speakers continue to play sound.</p>
<p>The solution, after much digging, is to add:</p>
<p><code>options snd-hda-intel model=ideapad</code></p>
<p>to /etc/modprobe.d/alsa-base.conf </p>
<p>I've put in a <a href="https://bugs.launchpad.net/ubuntu/+source/alsa-driver/+bug/680844">bug report</a>, so hopefully this can get a fix in Natty.</p>