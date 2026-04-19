---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Displaying EE mobile data usage in Conky
wordpress_id: 2746
wordpress_url: https://www.martineve.com/?p=2746
date: !binary |-
  MjAxMy0wNy0xNCAxNzowNzoxOSArMDIwMA==
date_gmt: !binary |-
  MjAxMy0wNy0xNCAxNjowNzoxOSArMDIwMA==
categories:
- Technology
tags:
- Technology
comments: []
doi: "https://doi.org/10.59348/xecrq-8qk94"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2013/07/14/displaying-ee-mobile-data-usage-in-conky"
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






