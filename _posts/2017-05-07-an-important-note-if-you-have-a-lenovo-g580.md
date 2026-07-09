---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2017/05/07/an-important-note-if-you-have-a-lenovo-g580
date: 2017-05-07
doi: https://doi.org/10.59348/dmq66-f5d26
image:
  feature: geek.png
layout: post
ogImage: geek.png
title: An important note if you have a Lenovo G580
---

The Lenovo G580 comes with Windows 8. It is possible to permanently lock yourself out of the operating system if you begin with a Microsoft account and migrate this to a local account. Further, you won't be able to rescue the system since _it is impossible to enter the BIOS setup in the machine's default state if you cannot login to Windows_.

To fix this:

1. Disable "fast boot" mode in Windows 8. You can do this in "Power Settings". If you don't do this, you can't modify the Windows disk partition when booting from a recovery USB.
2. [Update your BIOS](https://download.lenovo.com/consumer/mobiles/62cn97ww_64.exe). Do it now or you won't be able to unless you can still login to Windows 8.
3. Go into the BIOS (shutdown the machine then press the small button next to the power button and select "BIOS setup"). Then, set an administrator password in the BIOS settings. Then, "disable secure boot". This will allow you to boot from a recovery USB stick such as Kali or Ubuntu.

Urgh. A Catch-22 where Microsoft Windows corrupted a login (thanks, Microsoft) and a hardware defect stops you booting into a recovery medium (thanks, Lenovo).