---
archive: https://wayback.archive-it.org/22123/20241101171236/https://eve.gd/2025/10/04/pangolin-newt-gerbil-and-custom-ports
date: 2025-10-04
doi: https://doi.org/10.59348/hqabg-q5h89
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lvqzpul2p
image:
  feature: header_pangolin.png
layout: post
ogImage: images/header_pangolin.png
title: Pangolin, Newt, Gerbil and custom ports
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lvqzpul2p"
categories:
- Technology
kcworks: https://works.hcommons.org/records/ndyz1-7t012
references:
- title: 'GitHub - fosrl/pangolin: Modern networking and security platform providing secure access and connectivity to apps, infrastructure, and AI workloads. Connect and protect your users.'
  type: SoftwareSourceCode
  url: https://github.com/fosrl/pangolin
  isPartOf:
    name: GitHub
    type: WebSite
---

I have been playing around with [Pangolin](https://github.com/fosrl/pangolin), a really nice management system for exposing internal services over HTTPS.

However, I found that its internal wireguard networking does not play nicely if you already have another wireguard system, like tailscale, on the box. The solution was actually simple, but has a potential tripwire.

In your docker-compose.yml, set something like this under Gerbil's ports:

	- 51821:51821/udp

However, importantly: these ports must MATCH. You cannot have "- 51821:51820/udp" or similar. This will cause the Newt tunnels to fail.

Then, in pangolin/config/config.yml, make sure that the Gerbil port is set to 51821 or whatever your selected port is. Tada.