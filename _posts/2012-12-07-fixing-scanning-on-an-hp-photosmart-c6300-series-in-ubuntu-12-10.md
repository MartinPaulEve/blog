---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2012/12/07/fixing-scanning-on-an-hp-photosmart-c6300-series-in-ubuntu-12-10
categories:
- Linux
comments: []
date: 2012-12-07 09:17:49 +0100
date_gmt: 2012-12-07 09:17:49 +0100
doi: https://doi.org/10.59348/srhv6-07434
roguescholar: https://rogue-scholar.org/records/8sgnt-e2h87
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mhm4rmc2a
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Linux
- Ubuntu
- hplip
- xsane
- gscan2pdf
- scannning
title: Fixing scanning on an HP Photosmart C6300 series in Ubuntu 12.10
wordpress_id: 2518
wordpress_url: https://www.martineve.com/?p=2518
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mhm4rmc2a"
kcworks: https://works.hcommons.org/records/wc2he-eym35
---

<p>If you own an HP Photosmart C6300 series and upgraded to Ubuntu 12.10, you may have noticed that you are unable to set the scan resolution (DPI) in any of your programs. gscan2pdf has the scan resolution dropdown menu greyed out and you will be unable to get xsane to present you with a list of resolutions.</p>
<p>The answer is that the models.dat shipped with <a href="http://hplipopensource.com/hplip-web/release_notes.html">hplip versions under 3.12.10</a> contains <a href="https://bugs.mageia.org/show_bug.cgi?id=7637">an error</a>. To fix this, <a href="https://answers.launchpad.net/hplip/+question/208678">you simply need to edit</a> (as root) /usr/share/hplip/data/models/models.dat and change</p>
<p>scan-src=2<br />
to<br />
scan-src=1</p>
<p>in the section called photosmart_c6300_series (it has to be this section, not the generic photosmart section).</p>
<p>For those who don't know how to do this, if you open up a Terminal window and type the following, you should, once you've entered your password at the prompt, get a visual editor that will make this easier:</p>
{% highlight bash %}
sudo gedit /usr/share/hplip/data/models/models.dat
{% endhighlight %}

<p>Hope that helps somebody!</p>