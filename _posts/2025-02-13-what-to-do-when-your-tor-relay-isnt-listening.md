---
archive: https://wayback.archive-it.org/22123/20241101171236/https://eve.gd/2025/02/13/what-to-do-when-your-tor-relay-isnt-listening
date: 2025-02-13
doi: https://doi.org/10.59348/td9j1-v3t48
roguescholar: https://rogue-scholar.org/records/w6c29-r5s96
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lw7gg3o2f
image:
  feature: header_tor.png
layout: post
ogImage: images/header_tor.png
title: What to do when your Tor relay isn't listening
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lw7gg3o2f"
categories:
- Information Security
kcworks: https://works.hcommons.org/records/cb21r-h8083
---

I had a problem with [my Tor relay](/2025/02/06/going-dark-running-a-tor-relay-and-a-dark-web-version-of-this-site/) last night. For some reason, the application (daemon) started but then after about 5 seconds it stopped listening. The Tor Metrics site was displaying a red button saying my node was unreachable and when I did "sudo ss -ltp" I got nothing. The application literally wasn't "listening" (in network socket terms).

The answer was actually embarrassingly simple. If your Tor daemon stops listening, even if you can't find a log entry saying why, it _could_ be because you have burned through your entire traffic allocation for the accounting period. Increase the limit and try restarting it to avoid a red face.