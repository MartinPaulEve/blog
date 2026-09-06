---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2014/01/06/introducing-eprintscv-a-python-script-to-create-an-academic-web-cv-from-your-eprints-record
categories:
- Programming
comments: []
date: 2014-01-06 18:32:29 +0100
date_gmt: 2014-01-06 18:32:29 +0100
doi: https://doi.org/10.59348/y48wx-1fb70
roguescholar: https://rogue-scholar.org/records/zn85m-cb184
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mfs5u7d2q
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Python
- CV
- programming
- json
- eprints
title: 'Introducing eprintsCV: a python script to create an academic web CV from your
  eprints record'
wordpress_id: 2978
wordpress_url: https://www.martineve.com/?p=2978
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mfs5u7d2q"
kcworks: https://works.hcommons.org/records/38z01-5r023
references:
- title: 'GitHub - MartinPaulEve/eprintsCV: A script to generate a list of academic publications in a web/CV-friendly format for academic websites'
  type: SoftwareSourceCode
  url: https://github.com/MartinPaulEve/eprintsCV
  isPartOf:
    name: GitHub
    type: WebSite
---

<p>This afternoon, after an intense day of writing, I decided that I was finally fed up with maintaining so many different copies of my publication record. I have my institutional repository, my OpenOffice CV document, my Academia.edu profile and, of course, the <a href="https://www.martineve.com/c-v/">version on my own site</a>. I decided to do something about this.</p>
<p>Allow me to introduce <a href="https://github.com/MartinPaulEve/eprintsCV">eprintsCV</a>! This tool will grab your eprints articles, books, conference papers and book chapters and display them in an html list.</p>
<p>So, for my setup here (although I now need to convert the other sections), I have setup a cron job that runs:</p>

{% highlight bash %}
./eprintsCV.py eprints.lincoln.ac.uk 3354 "book,article,book_section,conference_item" > some_file.html
{% endhighlight %} 

<p>I've then simply used <a href="http://www.myvirtualdisplay.com/wordpress-projects/include_html/">include_html</a> to transclude the result.</p>
<p>Admittedly, there is risk (with a malicious eprints repository operator) for malicious insertion there, but I trust our lot.</p>
<p>If I had more inclination, I'd try and get this working with citeproc-py so that it could output in any format that was desired. As it stands, this is a pretty good solution for an hour-or-so's hacking.</p>