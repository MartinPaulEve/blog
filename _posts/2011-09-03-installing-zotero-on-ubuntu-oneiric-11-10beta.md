---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/09/03/installing-zotero-on-ubuntu-oneiric-11-10beta
categories:
- Linux
comments:
- author: Avram Lyon
  author_email: ajlyon@gmail.com
  author_url: ''
  content: 'Worth noting that Zotero 2.1.9 should work with Firefox 7, and that the
    Zotero 3.0 betas definitely do: http://www.zotero.org/support/firefox_beta_compatibility'
  date: 2011-09-04 05:10:00 +0200
  date_gmt: 2011-09-04 05:10:00 +0200
  id: 6526
- author: ''
  author_email: karcher@u.northwestern.edu
  author_url: ''
  content: I had also understood that Zotero doesn't rely on the sun java anymore
    - the LO/Ooo plugin 3.5 upwards uses Ooo's own java
  date: 2011-09-08 00:21:00 +0200
  date_gmt: 2011-09-08 00:21:00 +0200
  id: 6535
- author: William Ray Yeager
  author_email: wyeager@gmail.com
  author_url: ''
  content: I just upgraded to Oneiric and Zotero no longer plays nice with Libreoffice.
     I was using Libreoffice and Zotero 3.0 standalone on Kubuntu 11.4.  Under 11.10
    I've tried sun-java as well as openjdk.  The programs load as they did before
    but as soon as I try to use the Libreoffice extension to add a citation or refresh
    the bibliography, Libreoffice crashes.  Has anyone else had success?  Any recommendations?
  date: 2011-10-16 18:09:00 +0200
  date_gmt: 2011-10-16 18:09:00 +0200
  id: 6547
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  content: 'Try the following: 1.) Ensure that the correct JDK is selected in LO under
    Java options. 2.) Reinstall the citation plugin'
  date: 2011-10-16 19:45:00 +0200
  date_gmt: 2011-10-16 19:45:00 +0200
  id: 6548
date: 2011-09-03 15:34:52 +0200
date_gmt: 2011-09-03 15:34:52 +0200
doi: https://doi.org/10.59348/fqnpt-0e531
roguescholar: https://rogue-scholar.org/records/t7f63-pzg27
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mjyu33j2o
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- zotero
- Technology
title: Installing Zotero on Ubuntu Oneiric (11.10/Beta)
wordpress_id: 1449
wordpress_url: https://www.martineve.com/?p=1449
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mjyu33j2o"
kcworks: https://works.hcommons.org/records/ee8p7-10p43
---

<p>Following on from my previous <a href="https://www.martineve.com/2011/04/03/installing-zotero-on-ubuntu-natty-11-04beta/">guide to using Zotero in Ubuntu Natty</a>, I am pleased to present, here, the guide for Ubuntu 11.10: The Oneiric Ocelot. <s>The most crucial new addition is that, at the time of writing (September 2011), Zotero was unable to load in Firefox 7.0 beta.</s> Update: As of 9th of September, this is fixed. Zotero 2.1.10 will load in Firefox 7.</p>
<p><img src="https://www.martineve.com/wp-content/uploads/2011/09/Ubuntu-11.10-Oneiric-Ocelot.jpg" alt="Ubuntu-11.10-Oneiric-Ocelot" title="Ubuntu-11.10-Oneiric-Ocelot" width="400" height="153" class="alignnone size-full wp-image-1450" /></p>
<hr/>
<p>Since writing this article, a new version of Zotero has been published which renders the advice below unnecessary! Install Zotero 2.1.10 and LibreOffice plugin 3.5b, use the openjdk java environment and all should work. This makes Ubuntu Oneiric the easiest environment in which to install Zotero since Lucid.</p>
<p><s>1.) Add the Maverick partner repository:</p>
<p>Software Center -> Edit Menu -> Software Sources -> Other sources -> Add:</p>
<p>deb http://archive.canonical.com/ubuntu maverick partner</p>
<p>2.) Drop to a command prompt:</p>

{% highlight bash %}
    sudo apt-get update
    sudo apt-get install sun-java6-jre sun-java6-plugin
    sudo update-alternatives –config java
{% endhighlight %}


<p>If the last option prompts you to set a specific java configuration, ensure you select the Sun variant.</p>
<p><s>3.) <b>Downgrade Firefox</b>: at the time of writing, Firefox 7 is incompatible with Zotero. By this I don't mean that you can force it to work by disabling the compatibility check, I mean: it's *really* incompatible. Uninstall firefox:</p>

{% highlight bash %}
sudo apt-get remove firefox
{% endhighlight %}

<p>Visit <a href="http://www.mozilla.org/en-US/firefox/fx/">Mozilla's site</a> and install Firefox 6.</s> Update: As per above: this is no longer necessary in Zotero 2.1.10.</p>
<p>4.) Install the Zotero plugin from http://www.zotero.org/</p>
<p>5.) Install the <s>outdated</s> OpenOffice plugin,<s> not the most recent one: http://www.zotero.org/download/integration/Zotero-OpenOffice-Plugin-3.1b1.xpi</s> Update: As of 9th September, plugin 3.5b is confirmed working.</p>
<p>6.) After Firefox has restarted go to Zotero -> Preferences -> Cite tab.</p>
<p>In here, if needs be, change the OpenOffice parameters to the following:</p>
<p>UNO: file:///usr/lib/libreoffice/basis-link/ure-link/share/java/<br />
soffice binary: file:///usr/lib/libreoffice/program/</p>
<p>It is possible that you won't need to do this and that Zotero will correctly identify your LO directory.</p>
<p>7.) Click “install plugin”.</p>
<p>If this fails, go into LibreOffice, Tools menu -> Extension manager -> Add</p>
<p>Navigate to your firefox profile directory which will look like:</p>
<p>/home/yourusername/.mozilla/firefox/ALONGSTRINGOFLETTERS/extensions/zoteroOpenOfficeIntegration@zotero.org/install/</p>
<p>and manually add the .oxt file from within.</p>
<p>With any luck, you should be set. Worth also checking in LibreOffice -> Edit menu -> Preferences -> Java that you are using the Sun interpreter in LibreOffice.</s></p>