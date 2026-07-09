---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2021/08/20/replacing-openvpn-with-wireguard-including-on-synology-devices
date: 2021-08-20
doi: https://doi.org/10.59348/fggfg-qsy79
image:
  feature: geek.png
layout: post
ogImage: geek.png
title: Replacing OpenVPN with Wireguard, including on Synology devices
---

This week, I decided that I should move my VPN system that I run on all my devices to use the new Wireguard protocol, replacing the OpenVPN setup.

To do this, I used [NetMaker](https://github.com/gravitl/netmaker) for the configuration and setup and I have to say that it is superb. It works a treat on systems that have Wireguard easily installed and you then get a really neat web interface for administering clients. It's a far cry from the pain of setting up OpenVPN client push routines etc.

The one part where I fell down, though, was getting this to work on my Synology NAS boxes. Netmaker requires systemd, which is only available on Synology DSM 7. It also requires a kernel module to be loaded into the Synology box.

Here's [what I did](https://github.com/runfalk/synology-wireguard/issues/66#issuecomment-900438379) to get this working on a Denverton (DS1819+) box:

1. Upgrade to DSM 7 (this went _remarkably_ smoothly!)
2. Clone the DSM 7 kernel module from https://github.com/Matige/synology-wireguard/tree/DSM7.0
3. Run these commands:

<pre>
	git clone git@github.com:Matige/synology-wireguard.git
	cd synology-wireguard/
	git checkout DSM7.0
	sudo docker build -t synobuild .
	sudo docker run --rm --privileged --env PACKAGE_ARCH=&lt;arch&gt; --env DSM_VER=&lt;dsm-ver&gt; -v $(pwd)/artifacts:/result_spk synobuild
</pre>

In that last command, you need to replace arch with the correct architecture, as listed at [the official site](https://www.synology.com/en-global/knowledgebase/DSM/tutorial/General/What_kind_of_CPU_does_my_NAS_have). So, for my box, this should read "denverton". The DSM version is 7. My final command was sudo docker run --rm --privileged --env PACKAGE_ARCH=denverton --env DSM_VER=7.0 -v $(pwd)/artifacts:/result_spk synobuild.

4. Load the kernel module by copying the file to the shell and running (replacing with your actual filename in the first line):

<pre>
	sudo synopkg install WireGuard-denverton-1.0.20210606.spk
	sudo /var/packages/WireGuard/scripts/start
</pre>

You may also have to go into the package, in the DSM interface, find "Wireguard" and start it from there. If all goes to plan, when you run dmesg, you should see these lines:

		[ 7712.991744] wireguard: module verification failed: signature and/or required key missing - tainting kernel
		[ 7713.003067] wireguard: WireGuard 1.0.20210606 loaded. See www.wireguard.com for information.
		[ 7713.011640] wireguard: Copyright (C) 2015-2019 Jason A. Donenfeld <Jason@zx2c4.com>. All Rights Reserved.

5. Then do your usual Netclient install.
6. The final thing that you need to do is to remove the DNS setup. Edit /etc/netclient/netconfig-YOURNETWORKNAME and set "dnson" to "no". You should then do a sudo netclient push -n YOURNETWORKNAME. We do this because the Synology box doesn't have resolvectl for DNS pushing.

And then, tada, you should have a working Wireguard system.