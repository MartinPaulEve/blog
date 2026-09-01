---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2019/02/18/running-unoconv-on-ubuntu-1804-and-libreoffice-6
date: 2019-02-18
doi: https://doi.org/10.59348/j15vr-ybf31
roguescholar: https://rogue-scholar.org/records/2x77d-xy809
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m7d3vwy2h
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: Running unoconv on Ubuntu 18.04 and Libreoffice 6
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m7d3vwy2h"
categories:
- Linux
---

I've been having some serious problems running unoconv, the document conversion tool, on Ubuntu 18.04 using Libreoffice 6. This has been blocking the test suite (and basic functionality) in meTypeset from working.

Today, [I found the answer](https://github.com/dagwieers/unoconv/issues/454) with the help of the maintainer!

The basic gist is:

1. Uninstall the uno pip module everywhere. Use pip and pip3 to uninstall it. pip uninstall uno. pip3 uninstall uno.
2. Make sure that you have python3-uno installed via apt.
3. Make sure that the unoconv script itself is using the system-wide python3 executable. That is, the #! of /usr/bin/unoconv should read #!/usr/bin/python3

And now, it works!