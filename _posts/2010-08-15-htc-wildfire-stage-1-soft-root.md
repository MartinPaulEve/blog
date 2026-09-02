---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/08/15/htc-wildfire-stage-1-soft-root
categories:
- Information Security
comments:
- author: quidoh
  author_email: ''
  author_url: ''
  content: Awesome there is no beter word then awesome!It works fine. Thanks alot!
  date: 2010-08-15 10:36:39 +0200
  date_gmt: 2010-08-15 10:36:39 +0200
  id: 2
- author: Roffeboffe
  author_email: ''
  author_url: ''
  content: Works perfectly. :) Thanx a lot. Actually this is all I need. I can live
    with doing this every boot. Finally my daughter can get my old android which I
    have been promising her since I got the wildfire. Market enabler v3.0.8 works
    perfectly on the Wildfire also. :) Finally I have access to my paid apps again.
  date: 2010-08-15 12:31:03 +0200
  date_gmt: 2010-08-15 12:31:03 +0200
  id: 3
- author: Comfreak89
  author_email: ''
  author_url: ''
  content: 'If I will push the files to /sqlite_stmt_journals/  it says the following:user>adb
    shell$ push "C:\Users\user\Desktop\wildfire root\exploid" /sqlite_stmt_journals/push
    "C:\Users\user\Desktop\wildfire root\exploid" /sqlite_stmt_journals/push: permission
    deniedI start the cmd as administrator.Need help :)'
  date: 2010-08-15 21:21:36 +0200
  date_gmt: 2010-08-15 21:21:36 +0200
  id: 4
- author: Comfreak89
  author_email: ''
  author_url: ''
  content: got it...:)
  date: 2010-08-15 22:17:48 +0200
  date_gmt: 2010-08-15 22:17:48 +0200
  id: 5
- author: wildfireM
  author_email: ''
  author_url: ''
  content: thanks, Martin.  I need to add some fonts.  After making the above softroot,
    how I can add the fonts? If I do the following steps it fails already at adb root:adb
    root adb shell mount -o rw,remount -t yaffs2 /dev/block/mtdblock3 /system adb
    push c:\adb\ /system/fontsadb shell reboot Please advise, thanks !!!
  date: 2010-08-19 16:56:27 +0200
  date_gmt: 2010-08-19 16:56:27 +0200
  id: 6
- author: myjanky
  author_email: ''
  author_url: ''
  content: Hi, I am interested in compiling a version for the Motus MB300. After reviewing
    the exploid source and modifying the code to fit the Motus it fails somewhat.
    I can get /system rw but any attempt to issue another command boot loops the device.
    Any suggestions or help please advise.
  date: 2010-08-19 21:19:18 +0200
  date_gmt: 2010-08-19 21:19:18 +0200
  id: 7
- author: Martin Eve
  author_email: ''
  author_url: ''
  content: '@wildfireM and myjanky: you are both experiencing the problem of NAND
    protection. This soft-root does *not* bypass the protection on the flash memory.If
    you want to temporarily write to /system, you''ll need to mount /dev/block/mtdblock3
    somewhere else, then create a new directory and symlink the files *inside each
    directory of that mount* somewhere else, then mount bind this second directory
    over the top of /system. You can then put new files into that new directory and
    they will appear in /system/*'
  date: 2010-08-20 05:58:43 +0200
  date_gmt: 2010-08-20 05:58:43 +0200
  id: 8
- author: wildfireM
  author_email: ''
  author_url: ''
  content: Thank you for your answer, Can you please kindly let me know the instructions
    to write on the commandline, to do the above suggestions?
  date: 2010-08-20 06:21:03 +0200
  date_gmt: 2010-08-20 06:21:03 +0200
  id: 9
- author: wildfireM
  author_email: ''
  author_url: ''
  content: Martin, any news with the wildire root solving the NAND protection?thanks.
  date: 2010-09-08 13:26:04 +0200
  date_gmt: 2010-09-08 13:26:04 +0200
  id: 10
- author: Martin Eve
  author_email: ''
  author_url: ''
  content: Hi,Yes! Unrevoked has been able to fully root the Wildfire for a couple
    of weeks now!Best,Martin
  date: 2010-09-08 13:28:34 +0200
  date_gmt: 2010-09-08 13:28:34 +0200
  id: 11
- author: wildfireM
  author_email: ''
  author_url: ''
  content: Martin , thanks! I've downloaded and have the reflash.exe. Also installed
    the driver. But if I want only to install the fonts, what shall I do?
  date: 2010-09-08 14:04:36 +0200
  date_gmt: 2010-09-08 14:04:36 +0200
  id: 12
- author: Martin Eve
  author_email: ''
  author_url: ''
  content: You can't install fonts without full root access, so you need to root the
    device, reboot into recovery (the only mode where it's possible to modify /system)
    and push the fonts into the correct location. XDA forums might be a better place
    to ask for specific directions...
  date: 2010-09-08 14:08:01 +0200
  date_gmt: 2010-09-08 14:08:01 +0200
  id: 13
- author: wildfireM
  author_email: ''
  author_url: ''
  content: 'ok, I understand you mean this: adb push c:\adb\ /system/fonts/I dont
    know what hapenned...but my wildfire shows blankc screen, with the upper red light
    only, no mater which buttons I push. It is after I made a reflash.exe before.
    I was able to use it regular after this. Any advise?thanks.'
  date: 2010-09-08 14:43:43 +0200
  date_gmt: 2010-09-08 14:43:43 +0200
  id: 14
- author: Martin Eve
  author_email: ''
  author_url: ''
  content: I'm sorry, but I'm not a technical support forum, of which there are many
    on the internet. Take battery out. Restart, should be fine.
  date: 2010-09-08 14:58:04 +0200
  date_gmt: 2010-09-08 14:58:04 +0200
  id: 15
- author: wildfireM
  author_email: ''
  author_url: ''
  content: sorry, thank you.
  date: 2010-09-08 15:03:13 +0200
  date_gmt: 2010-09-08 15:03:13 +0200
  id: 16
- author: wildfireM
  author_email: ''
  author_url: ''
  content: 'Martin: thank you for all your help. I realy appreciate this! notr only
    for me. I succesfully pushed all the 8 fonts! still does not see the hebrew (did
    all needed), I''m sure something still missing but I''m on my way. Moshe'
  date: 2010-09-08 15:26:43 +0200
  date_gmt: 2010-09-08 15:26:43 +0200
  id: 17
- author: mightfly
  author_email: ''
  author_url: ''
  content: 'Martin, I tried your app on an unbranded WildfireKernel version2.6.29-c9472fc1but
    no joy I am afraid even after waiting 2, 10, 15s after the ''Force Close'' message.So
    I tried again with the manual approach.This comes up with:[-] creat: Permission
    deniedI can see that hotplug has already been created in /sqlite_stmt_journals
    with permissions-rw-r--r--Any ideas would be much appreciated, as I am keen to
    use sqlite3 on the device.'
  date: 2010-09-09 13:53:38 +0200
  date_gmt: 2010-09-09 13:53:38 +0200
  id: 18
- author: mightfly
  author_email: ''
  author_url: ''
  content: Sorry - I should have mentioned that I did this after installing the recent
    system update.  Is it possible that the exploit has been closed?
  date: 2010-09-09 15:44:11 +0200
  date_gmt: 2010-09-09 15:44:11 +0200
  id: 19
- author: Brian
  author_email: soccer_maniac26@hotmail.com
  author_url: ''
  content: I tried to download the softroot apk file but the link doesnt work
  date: 2010-09-25 07:23:38 +0200
  date_gmt: 2010-09-25 07:23:38 +0200
  id: 45
- author: Daniel
  author_email: pseudoesfera@gmail.com
  author_url: ''
  content: 'I''ve followed the instructions but every time I run the exploid file,
    I get a segmentation fault. I have to note that I''m running an updated version
    of the Firmware (2.1-update1) and Software Number: 1.25.162.1. I''d like to believe
    that this is the source of my problems rather that some mistake I might have done
    during the procedure. Is there any workarounds or a new version of that file?
    Thanks.'
  date: 2010-10-04 23:05:13 +0200
  date_gmt: 2010-10-04 23:05:13 +0200
  id: 84
- author: oli
  author_email: abuse@golka.priv.at
  author_url: http://goloka.priv.at
  content: "i test the one click soft root with the new 2.1 update version, make it
    5x no working, the superuser add dont work\r\ndont wont to make it this way, couse
    see other people also dont work\r\n\r\ndo you check this problem, or should i
    update to 2.2 and make root then ?\r\nwill update to 2.2 but hope that t-mobile
    released it next month, so dont wont to flash and get brake when i get the update
    in few months.\r\n\r\nplease help, want root, soft root for my wildfire, need
    swapper and other apps\r\n\r\nthy very much for help"
  date: 2010-10-12 17:35:22 +0200
  date_gmt: 2010-10-12 17:35:22 +0200
  id: 111
- author: oli
  author_email: abuse@golka.priv.at
  author_url: http://goloka.priv.at
  content: "sry my fault is that the superuser addon dont work and say he had a new
    version, make a .zip file on data card, but this file has 0mb and seems like broken\r\n\r\nhope
    you can help me android neewb"
  date: 2010-10-12 17:36:49 +0200
  date_gmt: 2010-10-12 17:36:49 +0200
  id: 112
- author: ledpepper
  author_email: ross.innes@ilabquality.com
  author_url: ''
  content: "Hi Martin,\r\n\r\nI have the same problem as Daniel and mightfly. I too
    am receiving segmentation faults.\r\n\r\nFirmware: 2.1 -update1\r\nBaseband: 13.53.55.24H_3.35.19.25\r\nKernel:
    2.6.29 htc-kernal@u18000-Build-149 #1\r\nBuild number: 1.37.405.1"
  date: 2010-12-03 09:04:26 +0100
  date_gmt: 2010-12-03 09:04:26 +0100
  id: 3689
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  content: "Hi,\r\n\r\nIt's supposed to segfault; that's the exploit doing its work.\r\n\r\nHowever,
    if you don't have root afterwards, then it seems likely that this solution is
    no longer working. Why not try unrevoked to get permanent root? It works fine,
    is pretty safe and a a much better solution than mine which was only ever meant
    as a temporary stop-gap.\r\n\r\nCheers,\r\n\r\nMartin"
  date: 2010-12-03 09:33:22 +0100
  date_gmt: 2010-12-03 09:33:22 +0100
  id: 3696
- author: daniel
  author_email: kosamu@hotmail.com
  author_url: ''
  content: Doe`s this work on 2.2.1??
  date: 2011-02-13 21:24:32 +0100
  date_gmt: 2011-02-13 21:24:32 +0100
  id: 6177
- author: Ankur
  author_email: ankur.nairit@gmail.com
  author_url: http://ankurtechblog.blogspot.com
  content: "Hi Martin Could you tell me if this procedure would work and get me a
    soft root on my wildfire running 2.2.1 and HBOOT &gt; 1.0.X ?\r\n I have tried
    a couple of tutorials but have been unable to get root access or S OFF ."
  date: 2011-05-10 07:46:41 +0200
  date_gmt: 2011-05-10 07:46:41 +0200
  id: 6291
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  content: Hi Ankur, I believe not as the exploit is designed for 2.1, not 2.2 and
    there are additional problems with rooting the later Wildfire versions. I believe
    the only root/S-OFF solution at the moment is the XTC clip. Best, Martin
  date: 2011-05-13 17:52:47 +0200
  date_gmt: 2011-05-13 17:52:47 +0200
  id: 6293
date: 2010-08-15 08:57:07 +0200
date_gmt: 2010-08-15 08:57:07 +0200
doi: https://doi.org/10.59348/vvye0-qq070
roguescholar: https://rogue-scholar.org/records/qhxp8-jja45
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mlte6aa2r
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Android
- root
- HTC
- Wildfire
title: HTC Wildfire Stage 1 Soft-Root
wordpress_id: 8
wordpress_url: http://new.martineve.com/?p=8
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mlte6aa2r"
kcworks: https://works.hcommons.org/records/dd62x-3bh86
---

<p><img src="https://www.martineve.com/wp-content/uploads/2010/08/superuser_request-300x225.jpg" alt="An HTC Wildfire displaying an Android Superuser permission request, beside a handwritten note reading Martin Eve" width="500" height="375"/><br />
<b>UPDATE 2013-06-30: I'm afraid that I've had to remove the below files as my host thinks they are a virus. Great. Anyway, this method has easily been surpassed by now.</b></p>
<p>This is a break from my customary blog posts on Thomas Pynchon and my university research to present a sample of one my other research interests in the realm of computer science and information security.
Google has, for a fair while now, been distributing their stripped down version of the Linux operating system -- Android -- on mobile devices. These devices are capable of running as fully fledged Linux distributions but for the fact that manufacturers lock down the phones and make it incredibly difficult to gain administrative priveleges on the devices.
As such, I have begun investigating ways by which to circumvent this ridiculous restriction of users' rights on their own devices; as the recent US Supreme Court ruling sensibly decreed: the devices are owned by the end-users, the end-users should be able to control what is run on such systems and circumventing the protection mechanisms on a device one owns is neither illegal, nor protected by the DMCA.
Recently, a group dubbed "The Android Exploid Crew" released an extremely clever piece of code for the Android operating system which exploits the hotplug system. Essentially, it manages to install itself as a callback function upon enable/disable of any hotplug device (wifi/bluetooth) which is executed with escalated priveleges. The original exploit copies itself to a new binary in /system/bin, the flash-memory filesystem which has been remounted read-write, and which is owned by the root account and has the setuid bit set.
Now: the recent HTC device, the Wildfire (codenamed: Buzz), has an interesting system of protection on the flash memory -- NAND protection. This means that, despite the read-write remount of the /system filesystem, any write to this area will result in the system spiralling out of memory, refusing the write and then rebooting. Obviously, this means that the exploit, in its original form, results in a crash and reboot.
I have now modified this exploit to perform differently so that it will work on the Wildfire.
I anticipate that the best usage for my work is as follows, which I may attempt to implement if I have time:
Setup application (can we run at startup?) checks for existence of /system/bin/su <br />If not existent, it unpacks su binary and exploid binary to /sqlite_stmt_journals <br />Runs exploit <br />Rebind mount /dev/block/mtdblock3 to /sqlite_stmt_journals/binmount <br />Symlinks all binaries from /sqlite_stmt_journals/binmount/bin to /sqlite_stmt_journals/newbin <br />Copies su to /sqlite_stmt_journals/newbin <br />Chmods/chowns /sqlite_stmt_journals/newbin to a safe combo <br />Mounts /sqlite_stmt_journals/newbin over the top of /system/bin <br />su will now function correctly
Anyway, I have achieved all this manually and now have at /system/bin/ the su binary and, linked into this, the Superuser.apk application!
Obligatory screenshot of barnacle wifi tether requesting superuser permissions attached.
So, anyway, to reproduce this, grab these files (source at the end of the post if you want to recompile):
<a href="http://www.martineve.com/wildfirestage1root/su">http://www.martineve.com/wildfirestage1root/su</a> <br /><a href="http://www.martineve.com/wildfirestage1root/busybox">http://www.martineve.com/wildfirestage1root/busybox</a> <br /><a href="http://www.martineve.com/wildfirestage1root/Superuser.apk">http://www.martineve.com/wildfirestage1root/Superuser.apk</a> <br /><a href="http://www.martineve.com/wildfirestage1root/exploid">http://www.martineve.com/wildfirestage1root/exploid</a>
ANY STEPS YOU TAKE FROM HEREON ARE YOUR OWN UNDERTAKING. I ACCEPT NO RESPONSIBILITY FOR A BRICKED DEVICE, EVEN THOUGH I PERSONALLY HAD NO PROBLEMS.
Setup adb <br />Push all the files to /sqlite_stmt_journals/ <br />Execute:
adb shell <br />cd /sqlite_stmt_journals <br />./exploid
Toggle your wifi on and off
Back at shell, execute:
mkdir binmount <br />mkdir newbin <br />chmod 755 ./busybox <br />./exploid <br />./busybox mount -r -t yaffs2 /dev/block/mtdblock3 ./binmount <br />./busybox ln -s /sqlite_stmt_journals/binmount/bin/* /sqlite_stmt_journals/newbin/ <br />./busybox cp ./su ./newbin/ <br />./busybox mount --bind /sqlite_stmt_journals/newbin /system/bin <br />./busybox cp ./Superuser.apk /data/app/ <br />./busybox rm ./exploid <br />./busybox rm ./su
You now have a rooted HTC Wildfire... until you reboot.
Source files: <br /><a href="http://www.martineve.com/wildfirestage1root/exploid.c">http://www.martineve.com/wildfirestage1root/exploid.c</a> <br /><a href="http://www.martineve.com/wildfirestage1root/makefile">http://www.martineve.com/wildfirestage1root/makefile</a> <br /><a href="http://forum.xda-developers.com/showthread.php?t=682828">http://forum.xda-developers.com/showthread.php?t=682828</a></p>