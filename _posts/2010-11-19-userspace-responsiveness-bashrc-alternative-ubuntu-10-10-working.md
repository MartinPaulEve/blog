---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/11/19/userspace-responsiveness-bashrc-alternative-ubuntu-10-10-working
categories:
- Technology
- Linux
comments:
- author: Alex Filonov
  author_email: muddlin@gmail.com
  author_url: ''
  content: "Maybe working on 10.10. But on 8.04 I'm getting:\r\n\r\n\r\nalex@gazelle:~$
    mkdir -p -m 0700 /dev/cgroup/cpu/user/$$ \r\nmkdir: cannot create directory `/dev/cgroup/cpu/user/6806':
    Invalid argument"
  date: 2010-12-08 02:39:56 +0100
  date_gmt: 2010-12-08 02:39:56 +0100
  id: 3982
- author: foobar
  author_email: totolepabo@yahoo.fr
  author_url: http://yahoo.fr
  content: "Please, can we stop this ? This \"incredible tuning\" is nothing but a
    pile of shit. It will ONLY work if you start ALL your processes from a terminal,
    or anything having a PS1 prompt.\r\n\r\nfoo@bar:~$ for PID in `cat /dev/cgroup/cpu/user/*/tasks`;do
    cut -f1 -d' ' /proc/$PID/cmdline;done\r\n\r\nbash\r\nbash\r\nscreen-Sfoo\r\nSCREEN-Sfoo\r\n/bin/bash\r\nrtorrent\r\nbash\r\nssh\r\nssh\r\n\r\nWOOOO
    i'm SO HAPPY my shells are more responsive now !!\r\n\r\nPlease learn a little
    bit people."
  date: 2011-02-08 22:25:15 +0100
  date_gmt: 2011-02-08 22:25:15 +0100
  id: 6172
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  content: "The only reason I approved this comment was so that your rudeness and
    unhelpful manner can be made visible. How on earth do you think that adopting
    such a condescending, sarcastic tone is likely to help anyone?\r\n\r\nIn response
    to your \"argument\" (not quite sure why I'm bothering) I never claimed otherwise.
    As is quite clearly discussed in the Slashdot comment thread, this patch mostly
    benefits those who run large compile jobs in the background. As I fall into that
    group (mostly compiling AOSP), I thought I would share the userspace solution
    to a patch that was accepted for kernel merge. Just because you have nothing better
    to do on the command line than run rtorrent doesn't mean the situation is the
    same for all of us."
  date: 2011-02-09 09:38:04 +0100
  date_gmt: 2011-02-09 09:38:04 +0100
  id: 6173
- author: foobar
  author_email: totolepabo@yahoo.fr
  author_url: http://yahoo.fr
  content: "I am really grateful you did your highness :)\r\n\r\nThe only reason i'm
    being so rude on this comment is that there's a BUNCH of blogs fapping to this
    while they don't have a clue of what it really does.\r\n\r\nNow, you _are_ right,
    this will effectively boost up shell jobs (or anything having its parent given
    a PS1), but unfortunately, not everyone catch this, and you can read pretty much
    everywhere \"WOW THIS IS INCREDIBLE, FIREFOX IS NOW SO MUCH RESPONSIVE ON UBUNTU
    !!1!\". That's called a \"placebo effect\".\r\n\r\nNevertheless, thank you for
    your reply (and no, i'm not being sarcastic here), it feels good to read some
    common sense.\r\n\r\nKeep up the good work !"
  date: 2011-02-09 21:44:55 +0100
  date_gmt: 2011-02-09 21:44:55 +0100
  id: 6174
- author: Martin Paul Eve
  author_email: martin@martineve.com
  author_url: ''
  content: Thanks for this reply; I'm sorry if my tone was also rude in the reply.
    I agree, there is a certain amount of misinformation circulating as to where this
    will benefit users -- many have also pointed out, though, that this mostly benefits...
    Linus and his usage model!
  date: 2011-02-10 08:26:49 +0100
  date_gmt: 2011-02-10 08:26:49 +0100
  id: 6175
date: 2010-11-19 19:49:03 +0100
date_gmt: 2010-11-19 19:49:03 +0100
doi: https://doi.org/10.59348/ptgaz-f7v52
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Technology
- Ubuntu
title: 'Userspace responsiveness .bashrc alternative (Ubuntu 10.10: Working)'
wordpress_id: 437
wordpress_url: http://www.martineve.com/?p=437
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mllxa6e2h"
---

<p>Recent discussion on the lkm has lead to Linus giving the go-ahead to a large kernel patch that massively increases responsiveness when multi-tasking on Linux desktop. A <a href="http://slashdot.org/story/10/11/18/2246213/Alternative-To-the-200-Line-Linux-Kernel-Patch">slashdot article</a> today also points out that the same result can be achieved by modifications userspace and that this is, indeed, how the patch was tested.</p>
<p>The original instructions can be found at <a href="http://www.webupd8.org/2010/11/alternative-to-200-lines-kernel-patch.html">webupd8</a>, but, for Ubuntu systems, they are incomplete.</p>
<p>Here's the correct information.</p>
<p>/etc/rc.local should contain:</p>
<p><code>mkdir -p /dev/cgroup/cpu<br />
mount -t cgroup cgroup /dev/cgroup/cpu -o cpu<br />
mkdir -m 0777 /dev/cgroup/cpu/user<br />
echo "/usr/local/sbin/cgroup_clean" > /dev/cgroup/cpu/release_agent</code></p>
<p>and should be executable (sudo chmod +x /etc/rc.local).</p>
<p>Your ~/.bashrc should contain:</p>
<p><code>if [ "$PS1" ] ; then<br />
   mkdir -p -m 0700 /dev/cgroup/cpu/user/$$ > /dev/null 2>&1<br />
   echo $$ > /dev/cgroup/cpu/user/$$/tasks<br />
   echo "1" > /dev/cgroup/cpu/user/$$/notify_on_release<br />
fi</code></p>
<p>directly at the top.</p>
<p>Finally (and this is where the original instructions were incomplete), /usr/local/sbin/cgroup_clean should contain:</p>
<p><code>#!/bin/sh<br />
if [ "$1" != "/user" ]; then<br />
rmdir /dev/cgroup/cpu/$1<br />
fi </code></p>
<p>as suggested by an <a href="http://www.webupd8.org/2010/11/alternative-to-200-lines-kernel-patch.html#comment-99182030">anonymous comment</a> on the original. Finally, ensure the cgroup cleanup script is executable: sudo chmod +x /usr/local/sbin/cgroup_clean</p>
<p>Reboot your system and you too can have an <a href="http://www.phoronix.com/scan.php?page=article&item=linux_2637_video&num=2">ultra-responsive desktop</a>!</p>