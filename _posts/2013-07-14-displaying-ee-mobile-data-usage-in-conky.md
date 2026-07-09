---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2013/07/14/displaying-ee-mobile-data-usage-in-conky
categories:
- Technology
comments: []
date: 2013-07-14 17:07:19 +0200
date_gmt: 2013-07-14 16:07:19 +0200
doi: https://doi.org/10.59348/xecrq-8qk94
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Technology
title: Displaying EE mobile data usage in Conky
wordpress_id: 2746
wordpress_url: https://www.martineve.com/?p=2746
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mgnw5tm2h"
---

<p>OK, this is probably one of the most specific posts I've ever written, but...</p>
<p>I wrote a bash script to automatically fetch and parse the currently used data on the 4G EE mobile network in the UK that can then be used with Conky. It's a compact one liner that looks like this:</p>

{% highlight bash %}
#!/bin/bash
wget -qO- http://add-on.ee.co.uk/status | awk -v OFS=' / ' -v ORS='' '/<span class="data-used">/{sub(/^[^0-9]*/, ""); dused=$0; match(dused, /^([0-9].?[0-9]?).+([0-9][^G]?[0-9]?)/, arr);} END {print arr[1], arr[2];}'
{% endhighlight %}

<p>You can then call this from a conkyrc file with something like this:</p>

{% highlight bash %}
${color #F09000}Mobile Usage${color #707070}:${color white} ${execi 900 ~/.scripts/getusage.sh}GB
{% endhighlight %}