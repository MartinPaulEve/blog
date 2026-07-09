---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/12/30/account-aggregation-with-uk-banks-and-a-free-software-lloyds-tsb-scraper
categories:
- Technology
comments: []
date: 2011-12-30 18:36:23 +0100
date_gmt: 2011-12-30 18:36:23 +0100
doi: https://doi.org/10.59348/wgvt6-f5q66
layout: post
published: true
status: publish
tags:
- software
- GPL
- Ruby
- Banking
title: Account aggregation with UK banks and a free software Lloyds TSB scraper
wordpress_id: 1705
wordpress_url: https://www.martineve.com/?p=1705
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mjbxtd72q"
---

<p>I thought it would be a good idea (New Year's resolutions and all that) to make sure I was on top of my finances this coming year. For that purpose, I began to investigate options to aggregate my accounts in one place. There were several online options, but I really disliked the idea of giving an online service my banking credentials. In fact, while Lloyds TSB claim this is alright ("2.7 We will not treat you as breaking your security obligations just because you use an aggregation service we do not provide.  A typical aggregation service allows you to view information about your accounts with different banks on a single website." <a href="http://www.lloydstsb.com/ib/registration_termsconditions.asp">http://www.lloydstsb.com/ib/registration_termsconditions.asp</a>) I still remain unconvinced. Other banks seem to outright prohibit it.</p>
<p>However, there's no reason I can't do this at home, in my encrypted setup, with some desktop software, right? So I tried GnuCash and (after much faffing using Wine on Ubuntu) Intuit Quicken. Neither could import or sync with any of my UK bank accounts. This got on my nerves.</p>
<p>Earlier today, in my quest to make this work, I found a (now outdated) Ruby script designed to login to Lloyds TSB and get your account info. (<a href="http://code.google.com/p/chrisroos/source/browse/trunk/banking-scripts/lloyds-statement-downloader/#lloyds-statement-downloader%253Fstate%253Dclosed">http://code.google.com/p/chrisroos/source/browse/trunk/banking-scripts/lloyds-statement-downloader/#lloyds-statement-downloader%253Fstate%253Dclosed</a>) I decided, today, to take this one step further and update the script.</p>
<p>With that said, then, I proudly present a very basic scraper for Lloyds TSB for your own, purely personal, use. It should work in any Ruby/Hpricot -supported environment. Instructions are in the README and the program is licensed under the GPL v3. <a href="https://github.com/MartinPaulEve/lloyds_tsb_scrape">https://github.com/MartinPaulEve/lloyds_tsb_scrape</a>.</p>
<p><i>Featured image by <a href="http://www.flickr.com/photos/loopzilla/">loopzilla</a> under a CC-BY-SA license.</i></p>