---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/12/30/using-unison-to-synchronize-and-backup-your-work-part-1
categories:
- Linux
comments:
- author: Naomi Jacobs
  author_email: naomijacobs10@gmail.com
  author_url: http://naomijacobs.wordpress.com/
  content: Exceptionally useful advice! I'll give it a go, although the process may
    be a bit more technical than I can cope with. Looks like it would be worth the
    effort, though. Thanks!
  date: 2010-12-30 17:43:40 +0100
  date_gmt: 2010-12-30 17:43:40 +0100
  id: 6034
date: 2010-12-30 08:21:18 +0100
last_modified_at: 2026-09-06
date_gmt: 2010-12-30 08:21:18 +0100
doi: https://doi.org/10.59348/rway8-gts85
roguescholar: https://rogue-scholar.org/records/2ztnh-ay275
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mlameom2h
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Backup
- PhD
- unison
- synchronization
- dropbox
title: Using Unison to synchronize and backup your work [Part 1]
wordpress_id: 500
wordpress_url: http://www.martineve.com/?p=500
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mlameom2h"
kcworks: https://works.hcommons.org/records/45b4g-rak53
references:
- title: Unison File Synchronizer
  type: WebPage
  url: http://www.cis.upenn.edu/~bcpierce/unison/
- title: Dropbox
  type: WebSite
  url: https://www.dropbox.com/referrals/NTEwNzk5NzEzOQ?src=global0
---

<p>Everybody yaks on about backup all the time, but few people actually have a viable setup. They say: "yes, I copy stuff to a USB pen". So, if you do that once a week, how much work would you lose if, just before you undertook the backup, your laptop was stolen? This is exactly what happened to me two months ago except that I had a rigorous backup procedure. I left the British Library and was, one hour later, without my laptop. I bought a new laptop the next day and 6 hours after purchase had the entire thing back up and running and had lost no work. Nothing. This was because I use a system called <a href="http://www.cis.upenn.edu/~bcpierce/unison/">Unison</a> to synchronize and backup my work.</p>
<p><a href="http://www.martineve.com/2010/12/30/using-unison-to-synchronize-and-backup-your-work-part-1/unison/" rel="attachment wp-att-501"><img src="http://www.martineve.com/wp-content/uploads/2010/12/Unison.png" alt="Unison screenshot" title="Unison" width="668" height="460" class="alignnone size-full wp-image-501" /></a></p>
<p><strong>Terminology and Background</strong><br />
There's a few pieces of jargon that need clarification before continuing onto the howto portion of this post. It's also worth noting that I am using Ubuntu Linux as my operating system, but I have used Unison successfully on Windows before. There are also Mac OSX binaries.</p>
<p><em>Synchronization</em> is the process of making changes on multiple machines and reconciling them.<br />
<em>Backup</em> is the process of archiving a copy of your work to prevent against accidental deletion.<br />
<em>Unison</em> is a cross-platform, open source, free file synchronization utility.<br />
<em>SSH</em> is a secure means to access a remote system over the internet.<br />
<em>Dropbox</em> is a free cloud storage solution.</p>
<p><strong>HOWTO use Unison to backup to Dropbox</strong><br />
This is the easier of two methods, the second of which (SSH) I may well return to in a later post, and allows you to synchronize your work to a Dropbox account which, for many people with under 2GB of work, will be entirely free. Note well, you should <strong>never</strong> use Dropbox as your primary/only storage location. It can do odd things to your files and also makes you overly reliant on the cloud.</p>
<ol>
<li>Sign-up for a <a href="https://www.dropbox.com/referrals/NTEwNzk5NzEzOQ?src=global0">Dropbox account</a> and install the client. Make a note of the location of your Dropbox directory.</li>
<li><a href="http://www.cis.upenn.edu/~bcpierce/unison/download.html">Download a copy of Unison</a> and install this somewhere on your environment path. Windows users should see the <a href="http://support.microsoft.com/kb/310519">Microsoft Help article on PATH</a> for information on this.</li>
<li>Write a unison preferences file and put this somewhere Unison can find it (on *Nix systems this will be under ~/.unison/dropbox.prf, on Windows it will be: C:\Documents and Settings\UserName\.unison\dropbox.prf). Here's what mine looked like:</li>
</ol>

{% highlight bash %}
# Unison preferences file

root = /home/martin/
root = /home/martin/Dropbox/

path = Documents/Work/Uni
{% endhighlight %}

<p>After this, I had to create the directory structure inside my Dropbox folder: "Documents/Work/Uni" (on Windows, probably: "c:\My Documents\Work\Uni") -- subdirectories will be automatically created, but unless you specify the root in the config file as the entire directory you want to sync, you need to create the top level directories by hand.</p>
<p>Now, drop to a command prompt (on Windows: Start -> Run -> cmd) and type: unison dropbox</p>
<p>Unison will alert you that this is the first time it has been asked to synchronize and will begin indexing your files. If, when this is done, it looks like the synchronization is doing what you want, I'd recommend aborting (CTRL+C) and starting again as: unison dropbox -batch</p>
<p>The batch mode will automatically sync your changes without asking you to confirm each file.</p>
<p><a href="http://www.martineve.com/2010/12/30/using-unison-to-synchronize-and-backup-your-work-part-1/dropbox/" rel="attachment wp-att-508"><img src="http://www.martineve.com/wp-content/uploads/2010/12/Dropbox.png" alt="Dropbox Synchronizing" title="Dropbox" width="454" height="285" class="alignnone size-full wp-image-508" /></a></p>
<p>Tada! You've now synchronized your work to Dropbox and, if you look in your Dropbox client, you will see that it is uploading.</p>
<p>Now, you can make a shortcut on your desktop to this configuration which means that all it takes at the end of a day, or lunchtime, is to double click this to initiate your sync. Alternatively, you could setup a crontab on a Linux system, or a Schedule on Windows to automatically run the system for you, thus eliminating your need to worry.</p>
<p>The other great thing is that you can run this on multiple machines. I have a desktop and a laptop, but this isn't a problem as Unison is bi-directional. As soon as those new files from the laptop hit Dropbox, they will be downloaded onto my Desktop and, when I run Unison at home they will be re-synced back into my file system there. This has the additional advantage of everything being backed up in triplicate; it can withstand two points of failure (my laptop and desktop being stolen, my laptop being stolen and Dropbox being compromised etc.)</p>
<p>While this may seem fairly complex, it's a one-time setup procedure that you can then simply use indefinitely. It is, however, not strictly an adequate backup on its own as you could still accidentally delete a file and then synchronize. Therefore, in a follow-up post, I will be examining ways you can script yourself an adequate backup.</p>