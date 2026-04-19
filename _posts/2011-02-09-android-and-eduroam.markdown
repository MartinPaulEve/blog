---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Android and Eduroam
wordpress_id: 763
wordpress_url: https://www.martineve.com/?p=763
date: !binary |-
  MjAxMS0wMi0wOSAxMTo0MDoyMSArMDEwMA==
date_gmt: !binary |-
  MjAxMS0wMi0wOSAxMTo0MDoyMSArMDEwMA==
categories:
- Technology
- Android
- Academia
- Linux
tags:
- Android
- Linux
- Eduroam
- Routing
comments:
- id: 6194
  author: Mohammed Fahd
  author_email: mf240@sussex.ac.uk
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0wNiAxODoxOToxOSArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0wNiAxODoxOToxOSArMDEwMA==
  content: hi, i really need help connecting my x10i to sussex wifi. could plz provide
    me with step by step process for this..excuse for my lil knowledge abt connectivity..
- id: 6195
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0wNiAxODozMjozNCArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0wNiAxODozMjozNCArMDEwMA==
  content: ! 'Hi,
    How far have you got? Have you got the device on the network? If not, I''d recommend
    going to ITS support, as they will certainly be able to help with this stage (you
    need to add the MAC address under your ITS account, then use outer-id: other-os-user@sussex.ac.uk,
    inner-id: yourITSusername and then your password as the password). If you are
    connected, but have no connectivity to the internet, post back and I''ll give
    you info on how to get the routing working.
    Martin'
- id: 6196
  author: Mohammed Fahd
  author_email: mf240@sussex.ac.uk
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0wNiAyMDo1MzowMSArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0wNiAyMDo1MzowMSArMDEwMA==
  content: i got my phone registered on ITS.
- id: 6197
  author: Mohammed Fahd
  author_email: mf240@sussex.ac.uk
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0wNiAyMDo1MzoyMiArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0wNiAyMDo1MzoyMiArMDEwMA==
  content: i got my phone registered on ITS. and i jus rooted my phone as well
- id: 6198
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0wNiAyMDo1NzoyMiArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0wNiAyMDo1NzoyMiArMDEwMA==
  content: Hi, so are you still having problems, or all set now?
- id: 6199
  author: Mohammed Fahd
  author_email: mf240@sussex.ac.uk
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0wNiAyMTo0MzoyNyArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0wNiAyMTo0MzoyNyArMDEwMA==
  content: nope.. it so happens i  tried connecting it says obtaining adress but disconnects
    l8r on..
- id: 6200
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0wNiAyMTo0Njo0OCArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0wNiAyMTo0Njo0OCArMDEwMA==
  content: ! "What version of Android? (Also: this is not related to the problem documented
    in this post; in my case, I could get an address, connect, but not see any web
    pages).\r\n\r\nI'd still recommend going to ITS and asking them to do the initial
    setup; takes 15 mins."
- id: 6201
  author: Mohammed Fahd
  author_email: mf240@sussex.ac.uk
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0wNiAyMzoxNzo1OCArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0wNiAyMzoxNzo1OCArMDEwMA==
  content: it is running on 2.1-1..oh ok 'l look in to its 2mr.. i went thr initially
    regarding the client certificate as my phone did not accept .cer... i belive its
    .pfx cert so i downloaded that but now its asks for pswd..
- id: 6207
  author: Mohammed Fahd
  author_email: mf240@sussex.ac.uk
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0wNyAyMDowOTowMSArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0wNyAyMDowOTowMSArMDEwMA==
  content: hey sry for trouble again..i went to its ppl they to din know wat to do
    wid my prob..i think 'm going wrong at certificate part..cud u plz tel me wat
    kind of cert is required for x10? i think its .pfx format but it asks for pasword
    when i tried installin it on my phone...ITS folks din know wat to do..
- id: 6208
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0wNyAyMToyNjo0MiArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0wNyAyMToyNjo0MiArMDEwMA==
  content: ! "Hi; scrap the certificates -- you don't need to do it -- just use EAP-TTLS
    with MSCHAPv2 inner auth.\r\n\r\nPut your usernames in (remember other-os-user@sussex.ac.uk
    for outer identity, your ITS username for inner id) and, with any luck, it should
    work. (Provided you've added the MAC address)\r\n\r\nI've never used the certs
    on Android (although I'm on 2.3, Froyo) and it works fine (apart from the bug
    described in this post on some handsets)"
- id: 6210
  author: Mohammed Fahd
  author_email: mf240@sussex.ac.uk
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0wOCAxMjo1OToxNyArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0wOCAxMjo1OToxNyArMDEwMA==
  content: ok thnx..when u talk abt outer n inner identity..u mean when i input the
    setting for wifi thr r two things identiy and anonymus identity..is this wat u
    refering to?
- id: 6211
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0wOCAxMzowODozMyArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0wOCAxMzowODozMyArMDEwMA==
  content: ! "Hi,\r\n\r\nYes, my apologies:\r\n\r\nouter identity = anonymous identity
    (other-os-user@sussex.ac.uk)\r\ninner identity = identity (ITS username)\r\n\r\nBest,\r\n\r\nMartin"
- id: 6241
  author: Mohammed Fahd
  author_email: mohd_fahd87@hotmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0xNSAxNjoxNzo0NyArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0xNSAxNjoxNzo0NyArMDEwMA==
  content: ! "Hi martin,\n  i so far got it connected to wifi netwrk..but now the
    pages don load..so if u cud help me out in this regard..i gues this is similar
    to wat u posted on this site? cud u provide with detail info as 'm new to this
    congifuration stuff.."
- id: 6242
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0xNSAxNzozMzozMCArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0xNSAxNzozMzozMCArMDEwMA==
  content: ! "Hi,\r\n\r\nYou'll need a rooted device for this to work, but here goes:\r\n\r\nOk,
    so connect your device to your PC using the USB cable and select \"Mount as disk
    drive\".\r\n\r\nCreate a file on your device's SD card called \"push_routes.sh\"
    and put this in it:\r\n\r\nroute add 10.0.8.5 dev eth0\r\nroute add default gw
    10.0.8.5 dev eth0\r\n\r\nDownload \"Gscript lite\" from the Android Market.\r\n\r\nIn
    Gscript Lite add a new script, \"load from file\" the file you created on the
    SD card. Ensure the \"su\" tickbox is checked.\r\n\r\nNow, run that script and
    you should get internet.\r\n\r\nMight be worth me dropping an email to ITS to
    let them know that several people are having problems :/"
- id: 6243
  author: Mohammed Fahd
  author_email: mf240@sussex.ac.uk
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0xNSAxNzo1MDo1OSArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0xNSAxNzo1MDo1OSArMDEwMA==
  content: ok..wil give it a try..thnx for help..
- id: 6247
  author: Mohammed Fahd
  author_email: mf240@sussex.ac.uk
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0xOCAxNzoyMTowNyArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0xOCAxNzoyMTowNyArMDEwMA==
  content: ! "hi martin sry for this stupid questions.. but how do i creat a file
    with that  name? i can c an option for text document do i input this\r\nroute
    add 10.0.8.5 dev eth0\r\nroute add default gw 10.0.8.5 dev eth0\r\n \r\nand name
    that file?"
- id: 6248
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0xOCAxNzo0MzoxNyArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0xOCAxNzo0MzoxNyArMDEwMA==
  content: ! 'Hi,
    If you are on Windows (sorry, I don''t know the Mac equivalent), open notepad,
    paste those lines in, and then save the file as push_routes.sh on your phones''
    SD card.
    Best,
    Martin'
- id: 6249
  author: mohammed fahd
  author_email: mohd_fahd87@hotmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0xOSAxNDo0NToxNCArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0xOSAxNDo0NToxNCArMDEwMA==
  content: Hi martin I did as suggested but I cant find the file in gscript lite..
- id: 6250
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0xOSAxNTo0MjozNCArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0xOSAxNTo0MjozNCArMDEwMA==
  content: ! "Hi,\r\n\r\nHmm, that's odd; GScript Lite should find it if it ends on
    a file with a \".sh\" extension in the root of the SD card.\r\n\r\nAnyway, if
    it's really not showing up, you can manually type the lines into GScript Lite
    under \"Add script\"."
- id: 6251
  author: mohammed fahd
  author_email: mohd_fahd87@hotmail.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0xOSAxNjowMjo1MyArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0xOSAxNjowMjo1MyArMDEwMA==
  content: Now it says invalid script...im using x10i just in case is it has anything
    else that I need to do
- id: 6252
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0xOSAxNjowNTowMiArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0xOSAxNjowNTowMiArMDEwMA==
  content: Can I just confirm exactly what you have put in the script?
- id: 6253
  author: Mohammed Fahd
  author_email: mf240@sussex.ac.uk
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0xOSAyMDo0MzozMiArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0xOSAyMDo0MzozMiArMDEwMA==
  content: ! "route add 10.0.8.5 dev eth0\r\nroute add default gw 10.0.8.5 dev eth0"
- id: 6254
  author: Mohammed Fahd
  author_email: mf240@sussex.ac.uk
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0xOSAyMTowMjoyNSArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0xOSAyMTowMjoyNSArMDEwMA==
  content: ! "it says \r\n invalid argument\r\n no such device"
- id: 6256
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  date: !binary |-
    MjAxMS0wMy0yMiAxNjoxMzozNSArMDEwMA==
  date_gmt: !binary |-
    MjAxMS0wMy0yMiAxNjoxMzozNSArMDEwMA==
  content: ! 'Ah, now that''s a useful error. It seems, in your case, that the device
    "eth0" (which on mine is the name of the ethernet card) is not correct.
    1.) Is wifi enabled?
    2.) If it is and still doesn''t work, try replacing every instance of "eth0" with
    "tiwlan0"
    If that doesn''t work, finding out the name of the device is a pain (have to install
    busybox, then use busybox''s ifconfig to list devices)'
- id: 6634
  author: IT Services (Sussex)
  author_email: ''
  author_url: http://twitter.com/ITServices
  date: !binary |-
    MjAxMi0wMi0xMCAxMjoxOTowMCArMDEwMA==
  date_gmt: !binary |-
    MjAxMi0wMi0xMCAxMjoxOTowMCArMDEwMA==
  content: ! 'just to be a security nerd..the certificates are not needed for connection
    but if you don''t use them, you''re theoretically vulnerable to "evil twin" or
    "man in the middle" attacks - e.g. see http://en.wikipedia.org/wiki/Evil_twin_(wireless_networks).
    Shame it''s so difficult to get a cert onto an Android phone in some cases but
    if you can get onto the internet (e.g. by using 3G), then you can usually download
    the certs needed for Sussex from: http://www.sussex.ac.uk/its/certs'
- id: 6635
  author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  date: !binary |-
    MjAxMi0wMi0xMCAxMjoyODowMCArMDEwMA==
  date_gmt: !binary |-
    MjAxMi0wMi0xMCAxMjoyODowMCArMDEwMA==
  content: Yes, indeed. I have, since this point, managed to get the certs onto the
    device but it is a complete faff! Thanks for the response.
doi: "https://doi.org/10.59348/draft-rmd94"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/02/09/android-and-eduroam"
---
<div><img src="https://www.martineve.com/wp-content/uploads/2011/02/eduroam-logo.gif" alt="Eduroam" title="eduroam-logo" width="601" height="260" class="alignnone size-full wp-image-764" /></div>
<p><i>Image credit: Copyright Eduroam, used here as fair use to indicate the network in question.</i></p>
<p>It seems there's a few bugs in various Android variants that prevent a valid routing table being setup when connecting to an institutional eduroam network. The problem, which I have seen people reporting on XDA, occurs when you can get onto the wifi network, but still no resources are available.</p>
<p>You'll need a rooted device to fix this, and it's a clumsy workaround, but here's what I did on the University of Sussex campus.</p>
<p>1.) Dump a valid routing table from a device that works:</p>
<pre>
sudo route
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
10.0.8.5        *               255.255.255.255 UH    0      0        0 wlan0
link-local      *               255.255.0.0     U     1000   0        0 wlan0
default         10.0.8.5        0.0.0.0         UG    0      0        0 wlan0
</pre>
<p>2.) Shell into your android device and check the routing table there:</p>
<pre>
route
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
</pre>
<p>What a surprise, it's empty.</p>
<p>3.) Add a route to your gateway and then a default route using the gateway</p>
<pre>
route add 10.0.8.5 dev eth0
route add default gw 10.0.8.5 dev eth0
route
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
10.0.8.5        *               255.255.255.255 UH    0      0        0 eth0
default         10.0.8.5        0.0.0.0         UG    0      0        0 eth0
</pre>
<p>Hurrah! You are now connected. It's probably worth putting this in a script which you can automatically run with Script Kitty or the such like.</p>
<p>4.) Test connectivity</p>
<pre>
ping google.com
PING google.com (74.125.230.116) 56(84) bytes of data.
64 bytes from 74.125.230.116: icmp_seq=1 ttl=53 time=14.8 ms
</pre>





