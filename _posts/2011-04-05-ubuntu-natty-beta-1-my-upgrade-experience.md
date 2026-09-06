---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/04/05/ubuntu-natty-beta-1-my-upgrade-experience
categories:
- Linux
comments: []
date: 2011-04-05 09:10:00 +0200
last_modified_at: 2026-09-06
date_gmt: 2011-04-05 09:10:00 +0200
doi: https://doi.org/10.59348/9fmvk-qwg92
roguescholar: https://rogue-scholar.org/records/v0dgt-f9z57
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mkguopl2n
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Ubuntu
- Unity
title: 'Ubuntu Natty Beta 1: My Upgrade Experience'
wordpress_id: 936
wordpress_url: https://www.martineve.com/?p=936
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mkguopl2n"
kcworks: https://works.hcommons.org/records/wbd4j-rpa22
references:
- title: DesktopExperienceTeam/UnityWithFglrxBeta
  type: WebPage
  url: https://wiki.ubuntu.com/DesktopExperienceTeam/UnityWithFglrxBeta
  isPartOf:
    name: Ubuntu Wiki
    type: WebSite
- http://kb2.adobe.com/cps/492/cpsid_49267.html # Adobe KB article: AIR ELS storage fix
- title: 'Bug #751067 "Colors are mangled in Natty"'
  type: WebPage
  url: https://bugs.launchpad.net/ubuntu/+source/thunderbird/+bug/751067
  isPartOf:
    name: Launchpad
    type: WebSite
---

<p>I thought I'd share here some of the trials and tribulations I experienced in last night's upgrade to Ubuntu 11.04, Natty Narwhal.</p>
<p><img src="https://www.martineve.com/wp-content/uploads/2011/04/unity.jpg" alt="Ubuntu Unity" title="Ubuntu Unity" width="750" height="422" class="alignnone size-full wp-image-939" /></p>
<h3>flgrx driver problems</h3>
<p>Using the flgrx driver most of my desktop was black, with occasional bits of the background visible. I solved this by selecting "Classic Session" at the GDM prompt and following the instructions at http://ubuntuforums.org/showpost.php?p=10618166&postcount=1 and https://wiki.ubuntu.com/DesktopExperienceTeam/UnityWithFglrxBeta</p>
<p>In short:<br />
Enable restricted in your apt sources list</p>
<p>and</p>
<blockquote><p>sudo apt-add-repository ppa://unity/daily</p></blockquote>
<p>Then:</p>
<blockquote><p>sudo apt-get update<br />
sudo apt-get upgrade<br />
sudo apt-get install fglrx<br />
sudo update-alternatives --config gl_conf (and select the line with fglrx)<br />
sudo update-initramfs -u</p></blockquote>
<p>Reboot.</p>
<h3>Tweetdeck errors</h3>
<p>I received errors from Adobe AIR/Tweetdeck saying the secure storage system was out of action. I solved this by using the instructions at http://kb2.adobe.com/cps/492/cpsid_49267.html:</p>
<blockquote><p>rm -rf ~/.appdata/Adobe/AIR/ELS</p></blockquote>
<p>You'll have to re-enter your account details.</p>
<h3>Mangled colours</h3>
<p>I reported this as a bug in Thunderbird, because that's where I first noticed it (<a href="https://bugs.launchpad.net/ubuntu/+source/thunderbird/+bug/751067">https://bugs.launchpad.net/ubuntu/+source/thunderbird/+bug/751067</a>), but it actually seems to affect every application, but only in certain places, most specifically in the display of PNG files. Basically, some of my colours are really messed up. This could be because of the experimental flgrx driver, but time will tell.</p>
<h3>The good</h3>
<p>To not be entirely negative... I love Unity! Have so much more space available on my desktop to do my actual work although, in its present state, the entire system feels very sluggish compared to traditional Gnome.</p>