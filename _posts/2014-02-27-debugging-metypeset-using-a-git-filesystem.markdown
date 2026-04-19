---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Debugging meTypeset using a git filesystem
wordpress_id: 3047
wordpress_url: https://www.martineve.com/?p=3047
date: !binary |-
  MjAxNC0wMi0yNyAxNTo1NTo1MiArMDEwMA==
date_gmt: !binary |-
  MjAxNC0wMi0yNyAxNTo1NTo1MiArMDEwMA==
categories:
- Technology
- Open Access
tags:
- OA
comments: []
doi: "https://doi.org/10.59348/5vnbp-c9c33"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2014/02/27/debugging-metypeset-using-a-git-filesystem"
---
<div style="clear:both"/>
<h1>Debugging a text-based transcoder</h1>
<p>meTypeset is, in essence, a transcoder for text. While “transcode” is usually used in a multimedia context, we are transcoding from one XML specification (Microsoft's OOXML) to another (JATS XML). This involves several stages of action:</p>
<ul>
<li>Unzip the document</li>
<li>Perform XSLT transforms to an intermediate format</li>
<li>Do some logic-based guesswork on what the author might have meant with their strange formatting</li>
<li>Transform to NLM/JATS</li>
</ul>
<p>There is potential for unexpected results at every stage of this process.</p>
<h1>Enter git debug filesystem</h1>
<p>While it is possible, when developing, to step through most of the processes, because we have multiple portions of the transform handled by different technologies, it is often difficult to pinpoint the stage at which something went wrong. For instance: if the NLM isn't right, was the TEI right? If the TEI isn't right, was it right before we put it through python (and which module messed it up?)</p>
<p>To solve this, when meTypeset is passed the debug flag (“-d” or “--debug”) it will now initialize all of its output directories as git repositories and regularly commit after each module has performed its transforms, thereby providing an easy way of logging in any environment (and cloning the output to another machine). As a self-contained filesystem, git is ideal for this kind of work. It adds very little overhead (either in terms of space or processing time) and makes life a lot easier in this kind of debug work. You can see the implementation of this in GitPython in the dev branch of the project.</p>
<h1>Cite this article</h1>
<p>Please include the DOI in your citation: <a href="http://dx.doi.org/10.6084/m9.figshare.946260">http://dx.doi.org/10.6084/m9.figshare.946260</a><br />
You can <a href="https://www.martineve.com/lens-martineve/index.html?url=https://www.martineve.com/lens-martineve/data/2014-02-27.xml">view this post's XML with lens</a>.</p>





