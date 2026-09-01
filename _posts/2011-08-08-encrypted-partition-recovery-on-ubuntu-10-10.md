---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/08/08/encrypted-partition-recovery-on-ubuntu-10-10
categories:
- Linux
- Information Security
comments: []
date: 2011-08-08 07:26:56 +0200
date_gmt: 2011-08-08 07:26:56 +0200
doi: https://doi.org/10.59348/4f2h4-t8865
roguescholar: https://rogue-scholar.org/records/y2gey-arz83
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mk2w5do2t
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Linux
- security
- Encryption
- Recovery
title: Encrypted Partition Recovery on Ubuntu 10.10
wordpress_id: 1401
wordpress_url: https://www.martineve.com/?p=1401
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mk2w5do2t"
---

<p>The other day I was installing Xubuntu 10.10 onto an old Mac G4 Powerbook and got the keyboard layout wrong. I had encrypted the entire disk and so, with the keyboard mapped entirely incorrectly ("j" was enter), I was unable to unlock the disk to continue.</p>
<p>To solve this, I booted off the alternate CD and entered a recovery shell, hoping this would ask me to unlock the disk. Sadly, no luck, it dumped me to a minimal BusyBox command shell to work out the unlock procedure myself. Here's how I did it. Please note, I can take no responsibility if these instructions cause damage to your system; they didn't for me, but if you don't know what you are doing, you could lose data.</p>
<p>Many of these instructions are derived from the <a href="http://wiki.debian.org/DebianInstaller/Rescue/Crypto">Debian crypto rescue</a> document.</p>
<h4>Enable LUKS Crypto</h4>
<p>Execute the following commands in the rescue prompt. One or more may fail, this shouldn't matter.</p>

{% highlight bash %}
anna-install crypto-modules
depmod -a
modprobe dm-mod
modprobe aes
{% endhighlight %}

<h4>Determine which partition needs unlocking</h4>
<p>Use fdisk (or on a Mac, parted/pdisk) to ascertain which is your root partition. You'll also need to determine your boot partition. I'm not going to go into details here as, if you don't know how to do this, you need to read more before you can safely complete this guide.</p>
<h4>Decrypt the partition</h4>
<p>Assuming your encrypted partition was hda4:</p>

{% highlight bash %}
cryptsetup luksOpen /dev/hda4 hda4_crypt
{% endhighlight %}

<h4>Determine which logical volumes exist within the group</h4>

{% highlight bash %}
lvdisplay | grep "LV Name"
{% endhighlight %}

<p>This produces an output like this:</p>

{% highlight bash %}

LV Name        /dev/myhost/root
LV Name        /dev/myhost/home
LV Name        /dev/myhost/swap_1

{% endhighlight %}

<p>As the group name is "myhost" in the above example (it will be different for you), enable the logical volume with:</p>

{% highlight bash %}
vgchange -a y myhost
{% endhighlight %}

<h4>Mount partitions</h4>
<p>Obviously substituting "myhost" for the group and "sda1" for your boot partition</p>

{% highlight bash %}

mkdir /target
mount /dev/myhost/root /target
mount /dev/myhost/home /target/home
mount /dev/sda1 /target/boot
mount proc /target/proc -t proc
mount sysfs /target/sys -t sysfs
{% endhighlight %}

<p>Check that /target/etc/crypttab contains the correct name (in this example "myhost"). If it doesn't:</p>

{% highlight bash %}
dmsetup rename myhost name_according_to_crypttab
{% endhighlight %}

<p>Finally:</p>

{% highlight bash %}
chroot /target
{% endhighlight %}

<p>and if you want to reconfigure the keyboard, my entire reason for doing this:</p>

{% highlight bash %}
dpkg-reconfigure console-setup
{% endhighlight %}

<p><i>Featured image by <a href="http://www.flickr.com/photos/joncallas/">joncallas</a> under a CC-BY license.</i></p>