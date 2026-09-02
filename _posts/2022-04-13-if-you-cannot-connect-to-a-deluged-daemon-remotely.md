---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2022/04/13/if-you-cannot-connect-to-a-deluged-daemon-remotely
date: 2022-04-13
doi: https://doi.org/10.59348/4zgr8-exe20
roguescholar: https://rogue-scholar.org/records/10c7f-b3v94
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lzbrd322h
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: If you cannot connect to a deluged daemon remotely
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lzbrd322h"
categories:
- Linux
kcworks: https://works.hcommons.org/records/zmbdt-2a742
---

I had a setup of deluge running on a remote box as a daemon. I had verified the credentials were all OK, the port forwarding was setup, the daemon was running and listening. But I couldn't connect remotely.

CHECK THE VERSION OF DELUGED THAT YOU ARE RUNNING!

If you are running deluged 1.3.x and trying to connect with deluge 2.x, it will report that the remote server is not running. It won't tell you that the server is on a different version or anything helpful like that, sadly.