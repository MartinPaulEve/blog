---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2016/06/19/cassius-now-supports-full-headless-pdf-creation-from-jats
date: 2016-06-19
doi: https://doi.org/10.59348/6rkea-5q639
roguescholar: https://rogue-scholar.org/records/zz4tf-61066
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mbcoatm2n
image:
  feature: post_images/CaSSius.png
layout: post
ogImage: post_images/CaSSius.png
title: CaSSius now supports full headless PDF creation from JATS XML
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mbcoatm2n"
categories:
- Publishing Technology
- Programming
kcworks: https://works.hcommons.org/records/gprpj-p6z76
references:
- https://github.com/MartinPaulEve/CaSSius # CaSSius PDF typesetter GitHub repo
- https://github.com/FremyCompany/css-regions-polyfill # Remy CSS regions polyfill GitHub repo
---

[CaSSius is the PDF typesetter](https://github.com/MartinPaulEve/CaSSius) that I am building as part of my work for the Andrew W. Mellon Foundation grant to Birkbeck for the Open Library of Humanities. CaSSius allows for [true XML-first workflows](https://www.martineve.com/2015/07/20/building-a-real-xml-first-workflow-for-scholarly-typesetting/).

#Background
CaSSius is called CaSSius (with that capitalization) because it uses a feature of "CSS" called Regions. Regions are an experimental and unsupported technology that allow the specification of "regions" (unsurprisingly) between which you can flow text. So, imagine you had an unspecified quantity of text. What you want to do is to create enough A4 pages that this content can be flowed between. CSS Regions theoretically allows us to do this. We can specify A4 regions (pages) and tell the browser to flow text between them.

The way that CaSSius works is as follows:

1. We have a JATS XML import procedure (XSLT) that takes the XML and produces an HTML document that is marked up in a way that our javascript can understand.
2. The javascript calls [François Remy's polyfill](https://github.com/FremyCompany/css-regions-polyfill) that adds in support for regions to any WebKit browser (more on this below)
3. Our javascript then waits (not very patiently) for the polyfill to do its job. Once that's done, our javascript calculates whether we need more or fewer pages and adds or subtracts them as necessary.

This works fine in a browser and has done for some time. It creates nicely printable documents. But, what we couldn't do, was just have a neat tool that we can run from the command line that will produce the PDF. I didn't know why or what was causing this, only that when run in Chrome or Firefox, all was fine, but the second we were on the command line, a 25 page document would take upwards of 10 minutes to build.

#The fix

Until today, I had about 90% of this project in a good state. As above, what I couldn't get to work, though, was any kind of command-line tool to print a PDF.Every single implementation would crash. I've spent days on end thinking about how to fix this and hit a dead end every time. Except today, when I refused to be defeated and started to dig into the polyfill code.

It turns out that the problem was that the polyfill was exponentially passing the * selector to various match functions as the document grew, thereby consuming system resources and eventually dying hard, with no vengeance.

A simple check to ensure that neither \* nor \*, were added to any match tests did the trick:

    if(selector != "*" && selector.indexOf("*,") < 0) {

#So now we can print from the command line
The output of:

    ./wkhtmltopdf --javascript-delay 15000 --no-stop-slow-scripts -L 0 -R 0 -B 0 -T 0 http://localhost:8000/ ~/result.pdf

[produces this PDF](/cassius/sample.pdf). Tada, JATS to PDF.