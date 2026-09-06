---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/11/16/wireless-when-housesitting-airmon-ng
categories:
- Information Security
- Linux
comments: []
date: 2010-11-16 08:38:38 +0100
last_modified_at: 2026-09-06
date_gmt: 2010-11-16 08:38:38 +0100
doi: https://doi.org/10.59348/1wtr5-d8396
roguescholar: https://rogue-scholar.org/records/5x39z-g9q53
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mlo5ysc2a
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- information security
- WEP
- password
title: Wireless when housesitting (airmon-ng)
wordpress_id: 408
wordpress_url: http://www.martineve.com/?p=408
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mlo5ysc2a"
kcworks: https://works.hcommons.org/records/zg5t5-5qc98
references:
- author: PreciousJohnDoe
  date: '2008-12-01'
  title: 'WIFI WEP Cracking with Aircrack-ng: Recover a Lost WEP Key'
  type: TechArticle
  url: http://www.brighthub.com/computing/smb-security/articles/17866.aspx
  isPartOf:
    name: BrightHub
    type: WebSite
---

<p>This weekend I was house- (and dog-) sitting for a friend and had been told that I could use the internet while at their place. Sadly, however, the way this was configured was a guest account added my friend's laptop and she had not left the WEP key for their router. I was unable to obtain the WEP key as Windows 7 encrypts this data and the guest account cannot decrypt it. As I had permission (and really wanted wireless on my own laptop for ssh etc.), I decided to crack the WEP key and wanted to share my experience.</p>
<p>For this to work you need to have at least one other computer that can connect to the router.</p>
<p>My hardware setup is a Toshiba Satellite laptop and the first thing I did was to install the requisite packages:</p>
<p><code>sudo apt-get install aircrack-ng</code></p>
<p>I then determined the name of my wifi adapter by using:</p>
<p><code>iwconfig</code></p>
<p>and noting down the output (for example):</p>
<blockquote><p>martin@theoria:~/.config$ iwconfig<br />
lo        no wireless extensions.</p>
<p>eth0      no wireless extensions.</p>
<p>wlan0     IEEE 802.11bg  ESSID:off/any<br />
          Mode:Managed  Access Point: Not-Associated   Tx-Power=15 dBm<br />
          Retry  long limit:7   RTS thr:off   Fragment thr:off<br />
          Power Management:off</p></blockquote>
<p>In this case, the adapter is called wlan0.</p>
<p>Now, if on standard Ubuntu 10.10, the next step is to disable wireless from network manager. Right click the network manager icon at the top right of the screen and deselect "Enable Wireless".</p>
<p>After that, you need to put the adapter into monitor mode and start airmon-ng:</p>
<p><code>sudo iwconfig wlan0 mode monitor<br />
sudo airmon-ng start wlan0</code></p>
<p>When that's up and running, you can do your initial reconnaissance work with:</p>
<p><code>airodump-ng wlan0</code></p>
<p>From here, note down the BSSID, Channel of the router you want to crack. Then, from the bottom, note the MAC address of the station that can connect to the router.</p>
<p>At this stage, we want to start collecting data:</p>
<p><code> airodump-ng --channel &lt;channel&gt; --bssid &lt;bssid of accesspoint&gt; -w ~/dump wlan0</code></p>
<p>The "data" column should start filling up (slowly) -- it needs to be at about 20,000 (preferably higher) before the key can be cracked. There are two ways to speed up this process. The first is to stge an ARP relay attack:</p>
<p><code>aireplay-ng --arpreplay -b &lt;bssid of accesspoint&gt; -h &lt;MAC address of client&gt; wlan0</code></p>
<p>although, note, I wasn't able to get this working.</p>
<p>The easier way, if you have access to the machine that can connect, is to just download a large (100mb+) file.</p>
<p>Once you've got 20,000 (or more) data values, you can use (in a separate terminal):</p>
<p><code>aircrack-ng -z -b &lt;bssid of the accesspoint&gt; ~/dump*.cap</code></p>
<p>to obtain the key. If it fails, collect more data and retry. Total time: 10 mins.</p>
<p>My original source for this howto was: <a href="http://www.brighthub.com/computing/smb-security/articles/17866.aspx">http://www.brighthub.com/computing/smb-security/articles/17866.aspx</a></p>