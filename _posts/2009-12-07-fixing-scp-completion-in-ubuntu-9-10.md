---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2009/12/07/fixing-scp-completion-in-ubuntu-9-10
categories:
- Linux
comments: []
date: 2009-12-07 12:41:39 +0100
date_gmt: 2009-12-07 12:41:39 +0100
doi: https://doi.org/10.59348/za1mv-m3617
layout: post
published: true
status: publish
tags:
- ssh
- Linux
- scp
title: Fixing scp completion in Ubuntu 9.10
wordpress_id: 229
wordpress_url: http://pro.grammatic.org/post-fixing-scp-completion-in-ubuntu-910-73.aspx
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mme35ml2n"
---

<p>Currently, owing to a bug, scp in Kubuntu and Ubuntu 9.10 (Karmic Koala) does not allow you to autocomplete remote directories (when you have a passwordless ssh setup, obviously).</p>
<p>While I have submitted a patch for review, this will not be backported into 9.10 and so, those who wish to have this functionality, should follow these steps:</p>
<p>Visit <a href="https://bugs.launchpad.net/ubuntu/karmic/+source/bash-completion/+bug/449349">this bug</a> to read about the problem. Note that this is a problem with bash-completion, not with scp itself.</p>
<p>Download my fix: <a href="http://launchpadlibrarian.net/35968198/ssh">bash-completion scp fix for Ubuntu 9.10</a>.</p>
<p>Backup your current file:</p>
<blockquote><p>sudo cp /etc/bash_completion.d/ssh ~/ssh_backup</p></blockquote>
<p>Copy the downloaded file to /etc/bash_completion.d/:</p>
<blockquote><p>sudo cp ./ssh /etc/bash_completion.d/</p></blockquote>
<p>Restart your bash session and you should have working scp remote completion! ie. scp remotehost:~/myfi[TAB] will complete to remotehost:/home/you/myfile.txt</p>
<p>Note: I am not responsible for any damage this causes - it is not an official patch and I am unable to provide tech support. If you find problems with the fix, please report them to the official bug posted above which is more likely to get a response.</p>
<p>If anything goes wrong, you can restore the old configuration using:</p>
<p>sudo cp ~/ssh_backup /etc/bash_completion.d/ssh</p>