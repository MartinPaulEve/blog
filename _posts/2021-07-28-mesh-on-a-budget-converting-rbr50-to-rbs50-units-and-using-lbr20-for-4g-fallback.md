---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2021/07/28/mesh-on-a-budget-converting-rbr50-to-rbs50-units-and-using-lbr20-for-4g-fallback
date: 2021-07-28
doi: https://doi.org/10.59348/a0583-f5w04
image:
  feature: header_4g.png
layout: post
ogImage: images/header_4g.png
title: 'Mesh on a budget: converting RBR50 to RBS50 units and using LBR20 for 4G fallback'
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m2vr3b32i"
---

For quite some time, I've wanted to have an internet system that could fallback to a 4G connection if the primary internet connection failed. This would be helpful for when I need to work/go to online meetings and my Virgin Media connection dies.

At the weekend, I found the LBR20 system, which is part of the Netgear Orbi system. It has precisely this functionality. Anyway, I bought the router and a SIM-only 4G data card from Three in the UK. I can report that it works a treat -- it's connected to my Virgin Media broadband and, when that dies, it drops back onto the LTE/4G connection from the Nano SIM. As a slight "gotcha", the setup for using 3G/4G in failover mode only is under Advanced Settings. Odd, as this is, I would guess, how most people want to use it.

I wanted, though, to use this system as part of a mesh network. The LBR20 only works with the older, non-WiFi6 systems, so you need some RBS50 satellite units. The original mesh systems for Orbi usually come with an RBR50 (the router) and then a number of RBS50 (satellite) addons. (Don't bother getting the RBR20 and RBS20 units: the backhaul channel is much slower.)

Here's the challenge, though: the router units (RBR50) are _much cheaper_ than the satellite units (RBS50). You _cannot_, though, use an RBR50 as a satellite. Or so Netgear tell you...

After [much reading around](https://www.reddit.com/r/HomeNetworking/comments/e53qp6/convert_orbi_rbr50_router_to_orbi_rbs50_satellite/), I found out how to convert an RBR50 into an RBS50 and can confirm that this worked for me. Credit to jdhulme on reddit for the tips. Here's what I did. I give NO WARRANTY that this will work for you. You do it at your own risk. But it worked for me.

1. Download [firmware 2.1.4.16](https://kb.netgear.com/000059432/RBR50-RBS50-Firmware-Version-2-1-4-16) from Netgear for both the RBR50 and RBS50.

2. Connect the PC LAN port to the RBR50.

3. Go to the router homepage (usually http://192.168.1.1) and do the initial config/setup, skipping everything. It doesn't matter what your setup is here as it will be nuked shortly.

4. Flash the RBR50 to the RBR50 2.1.4.16 firmware.

5. Once restarted, go to http://192.168.1.1/debug.htm, login using either your password or the default: "admin" / "password" and then turn on telnet.

6. Telnet to 192.168.1.1 using same admin / password credentials.

7. In telnet execute (the bits BEFORE the bits in brackets):

<pre>
    cd /sbin  
    artmtd -r board_data (should be 1101 or 1201)  
    artmtd -r board_model_id (should be RBR50)  
    artmtd -w board_data 1102 (or use 1202 if step 2 showed 1201)  
    artmtd -w board_model_id RBS50
</pre>


8. Now, power off the RBR50. Then, holding down the reset button, turn it back on. Keep the reset button held down until the power light underneath flashes red. The router is now in recovery mode.

9. Put your LAN interface into manual, rather than DHCP, and set the IP to 192.168.1.2, Netmask 255.255.255.0.

10. Rename your RBS50 firmware '1.img'.

11. Use TFTP to 'put' the '1.img' file. On Linux this looks like this:

<pre>
    tftp  
    connect 192.168.1.1  
    binary  
    put 1.img  
</pre>

12. The router will accept the file and begin rebooting. 

13. Put your LAN interface back into DHCP.

14. Now wait. This took up to 12 minutes for me for the router to come back online. If you turn it off now, you might brick it.

15. When it comes back up, it _should_ be an RBS50! This works for me. I then upgraded to the latest RBS50 firmware and synced the 'satellite' to the network.

And... tada!

You can get the RBR50 much much cheaper than RBS50s, but the firmware can be grafted on to the RBR50. Please don't blame me if you brick yours, but this worked for me and was a fun afternoon project.