---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2016/05/11/hypothesis-v0814-error-oserror-errno-2-no-such-file-or-directory
date: 2016-05-11
doi: https://doi.org/10.59348/8hafg-2hk36
roguescholar: https://rogue-scholar.org/records/yavad-90003
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mbfslj32p
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: 'Hypothes.is v0.8.14 error: "OSError: [Errno 2] No such file or directory"'
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mbfslj32p"
categories:
- Programming
---

If you are attempting to build the dev setup for hypothes.is v0.8.14 and are receiving the error "OSError: [Errno 2] No such file or directory" whenever you request pages on the dev site, you need to install compass.

    sudo apt-get install ruby1.9.1-dev
    sudo gem install compass