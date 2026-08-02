---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2012/01/23/protecting-your-assets-backing-up-your-academic-work
categories:
- Technology
- Academia
- Teaching
comments:
- author: Steve Cooke
  author_email: stephen.cooke@manchester.ac.uk
  author_url: http://twitter.com/SteveCooke
  content: I've had two laptops stolen with work on them, and a critical hard-drive
    failure on a PC, and am yet to lose any work. My local work is synced between
    my laptop and desktop machines to online storage using Ubuntu One (I used to use
    Dropbox) - which has some very basic version control and ridiculously easy to
    set up. No cost outlay is required and no special knowledge required to set it
    up - but the result is a set-up similar to yours.
  date: 2012-01-23 13:37:00 +0100
  date_gmt: 2012-01-23 13:37:00 +0100
  id: 6598
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: https://www.martineve.com
  content: 'I find one the key problems to be that it is so much easier to set this
    up, at practically zero-cost, on *Nix systems. I''m also working entirely on GNU/Linux
    and I use Unison to sync between servers. '
  date: 2012-01-23 13:42:00 +0100
  date_gmt: 2012-01-23 13:42:00 +0100
  id: 6599
- author: Steve Cooke
  author_email: stephen.cooke@manchester.ac.uk
  author_url: http://twitter.com/SteveCooke
  content: Aye - it's much easier on a *nix based system, but you can use something
    like Dropbox on a Windows OS really easily and that easily has enough free storage
    for most. That too has some basic functionality for reverting to older versions
    of uploaded files.
  date: 2012-01-23 13:50:00 +0100
  date_gmt: 2012-01-23 13:50:00 +0100
  id: 6600
date: 2012-01-23 12:26:22 +0100
date_gmt: 2012-01-23 12:26:22 +0100
doi: https://doi.org/10.59348/kb0pp-6na29
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Technology
- Backup
- PhDchat
title: 'Protecting Your Assets: Backing up your Academic Work'
wordpress_id: 1859
wordpress_url: https://www.martineve.com/?p=1859
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7miz4uie2h"
---

<p>I will be running, on the 31st January, <a href="http://www.sussex.ac.uk/doctoralschool/internal/researcherdev/events/index.php?pageon=2&status=open">a workshop for Sussex researchers</a> on protecting their assets; aka. backing up their work.</p>
<p>After the first year of my Ph.D I had a nasty scare when my laptop was stolen on my journey home (I had a migraine, effectively passed out and didn't notice someone simply take my bag from beneath me on the train). This could have been dire. Fortunately, though, I take backup and encryption very seriously. I thought I'd share my backup plan.</p>
<p>The below diagram demonstrates the different backups I make. Each box on this network contains a full copy of my work. Communication between all channels is protected by SSL public-key encryption. The HDDs on the laptop and home machines are fully encrypted inside a LUKS container. Crashplan is a commercial service I use, based in the States in case of total failure of my system.</p>
<p><img src="https://www.martineve.com/wp-content/uploads/2012/01/Backup_Diagram-1024x676.png" alt="Network diagram of a backup setup linking a home computer, home server, laptop, remote web server, and CrashPlan cloud service via the internet" title="Backup_Diagram" style="width:750px;" class="alignnone size-large wp-image-1860" /></p>
<p>The web server and old-PC-server automatically sync with the home computer. These updates propogate to CrashPlan automatically, which archives a 30-day history in case of accidental deletion. The laptop syncs manually to prevent against accidental loss. Furthermore, the home computer automatically archives the last week's worth of work via the following line called in a daily Cron script:</p>

{% highlight bash %}
rsync -avz --delete /home/martin/Documents/Work/Uni /home/martin/Documents/Backup/Work/$(date +%A)
{% endhighlight %}

<p>Anybody have any tips for improving, or can beat that for security?</p>