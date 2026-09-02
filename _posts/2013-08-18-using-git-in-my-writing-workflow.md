---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2013/08/18/using-git-in-my-writing-workflow
categories:
- Academia
- Technology
comments: []
date: 2013-08-18 14:45:52 +0200
date_gmt: 2013-08-18 13:45:52 +0200
doi: https://doi.org/10.59348/jm453-j8362
roguescholar: https://rogue-scholar.org/records/m940p-7xj17
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mges67k2u
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Writing
- git
title: Using git in my writing workflow
wordpress_id: 2808
wordpress_url: https://www.martineve.com/?p=2808
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mges67k2u"
kcworks: https://works.hcommons.org/records/pzx3y-kyq64
---

<p>My two spheres of interest -- difficult works of English literature and computer programming (OK, scholarly communications and publishing, also. OK, there are lots more spheres of interest) -- only intersect occasionally. However, in recent days I have been toying with the idea of using git to version control my writing. This isn't a new concept -- I've seen posts on the <a href="http://chronicle.com/blogs/profhacker/tag/git">Chronicle of HE about it</a> -- but I've yet to actually try it.</p>
<p>I think I first heard of git for academic writing through <a href="https://twitter.com/theNHJ">Newell Hampson-Jones</a> on Twitter and, I'm sorry to say, I was dismissive and sceptical. I struggle to remember what my exact thought process was, but I suspect it came from a viewpoint overly determined by the single-author model. I seemed unable to envision collaborative writing with git (mostly because I knew that Word and OpenOffice would yield blobs) and I also hadn't thought through how git could be useful to version both published artefacts and also my own internal versions. Bizarre.</p>
<p>Anyway, my current versioning system for documents is fairly horrendous. Every day I save a new file:</p>
<p>2013-08-18 - Document.odt</p>
<p>This means that, over the course of a book, I end up with a massive folder with a uniquely named version for every day's worth of work. This is all well and good, but it's clumsy.</p>
<p>Anyway, I'm going to try my next article with a git repository and wanted to share some setup tips.</p>
<p>First of all, please remember that git <b>IS NOT</b> github. Github is a web viewing service and collaboration facilitator for git repositories. I'm intending to work with local git repos as I'm not (yet) confident enough to publicly push my work in its versioned states (and I'm not sure anybody would be interested).</p>
<p>In any case, the key thing that will make this viable for me is having a way to see the diffs within an OpenOffice (or LibreOffice document), so I want to share how I've got that working (I'm using Linux Mint).</p>
<p>As per the <a href="https://git.wiki.kernel.org/index.php/GitTips#How_to_use_git_to_track_OpenDocument_.28OpenOffice.2C_Koffice.29_files.3F">gittips wiki</a>, I added the following to ~/.gitconfig</p>

{% highlight bash %}
[diff "odf"]
      textconv=odt2txt
{% endhighlight %}

<p>and ensured I had installed the odt2txt package ("sudo apt-get install odt2txt").</p>
<p>Then, once you've initialised the repository in the working directory for your new writing ("git init"), add the following to that repo's .gitattributes file:</p>

{% highlight bash %}
*.ods diff=odf
*.odt diff=odf
*.odp diff=odf
{% endhighlight %}

<p>Now git should be able to display the difference between commits in OpenOffice documents.</p>
<p>From there, I'd recommend gitk as a visual tool to see the diffs, but otherwise, I'm good to go!</p>