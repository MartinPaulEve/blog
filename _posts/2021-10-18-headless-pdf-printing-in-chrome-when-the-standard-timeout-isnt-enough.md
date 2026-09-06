---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2021/10/18/headless-pdf-printing-in-chrome-when-the-standard-timeout-isnt-enough
date: 2021-10-18
doi: https://doi.org/10.59348/1tta7-hnj71
roguescholar: https://rogue-scholar.org/records/qhesb-z5f63
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m2dur2c2r
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: 'Headless PDF printing in Chrome: when the standard timeout isn''t enough'
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m2dur2c2r"
categories:
- Programming
kcworks: https://works.hcommons.org/records/jvd1b-pw763
references:
- https://www.npmjs.com/package/html-pdf-chrome # html-pdf-chrome npm package
- title: GitHub - MartinPaulEve/cv
  type: SoftwareSourceCode
  url: https://github.com/MartinPaulEve/eprintsToCV
  isPartOf:
    name: GitHub
    type: WebSite
---

tl;dr: use the node.js module [html-pdf-chrome](https://www.npmjs.com/package/html-pdf-chrome) to print programmatically, not Chrome's built-in virtual-time-budget. See my [print.js file](https://github.com/MartinPaulEve/eprintsToCV/blob/master/print.js) for an example.

[My CV](https://eve.gd/c-v/Eve-CV.pdf) is generated automatically from Birkbeck's online repository. It uses a system that basically generates a paginated version of the CV in the browser, using CSS regions technologies, then does a headless print via Chrome. All [the source code is available for this](https://github.com/MartinPaulEve/eprintsToCV).

The problem is that Chrome has an option to wait until the page has fully rendered before printing. If you Google it, you'll get the answer that you should use the --run-all-compositor-stages-before-draw and --virtual-time-budget=10000 flags.

However, these do not work in the case of my CSS regions work. Regardless of how high I set the virtual time budget, on ultra-fast hardware, Chrome truncated the PDF.

I finally found a new solution in the node.js module [html-pdf-chrome](https://www.npmjs.com/package/html-pdf-chrome). You can see how this is now called inside my [print.js file](https://github.com/MartinPaulEve/eprintsToCV/blob/master/print.js) but, essentially, this allows for a timed completion trigger before it sets off the print. Setting this to 5000ms was more than adequate for my purpose.