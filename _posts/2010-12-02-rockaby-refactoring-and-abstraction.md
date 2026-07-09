---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/12/02/rockaby-refactoring-and-abstraction
categories:
- Literature
- Technology
- Django
comments: []
date: 2010-12-02 09:53:46 +0100
date_gmt: 2010-12-02 09:53:46 +0100
doi: https://doi.org/10.59348/xc4fv-rgq48
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- software
- rockaby
- django
title: Rockaby refactoring and abstraction
wordpress_id: 450
wordpress_url: http://www.martineve.com/?p=450
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mlk47iu2h"
---

<p><img class="alignnone" title="Rockaby" src="http://www.martineve.com/images/logo.png" alt="Rockaby Project" width="300" height="150" /></p>
<p>I've used the snow so far this morning to start some pythonic refactoring of Rockaby.</p>
<p>As I mentioned in my <a href="http://www.martineve.com/2010/11/19/rockaby-text-annotation-software-gpl-alpha-announcement/">project announcement</a>, Rockaby started life several years ago and it was a quick morning's worth of hacking about in .NET to build something that I thought nobody would ever see. As such, the code was hideous and messy. For the first code-drop, I simply transliterated the .NET code into Python/Django. This made for some grim view manipulation:</p>

{% highlight python %}
    # build an index of where this character occurs
    CharacterPages = []
    Parts = []

    # create a list of lists (to store page numbers)
    for counter in range(0,len(pynchon.parts.Parts.FormattedPartNames)):
        Parts.append([])

    for episode in episodes:
        if character_name in episode.characters:
            Parts[episode.part - 1].append(episode.episode)
            
            epChars = episode.characters.replace('\r\n', '\n').split('\n')
            for s in epChars:
                epCharsSplit = s.split('->')
                
                if epCharsSplit[0].lower() == character_name.lower():
                    splitPages = epCharsSplit[1].split(',')
                    
                    for pageNum in splitPages:
                        CharacterPages.append(pageNum)
                        
    ret = ''

    for counter in range(0,len(pynchon.parts.Parts.FormattedPartNames)):
        part = Parts[counter]
        
        part.sort()
        
        if (len(part) > 0):
            ret = ret + '<p class="p1"><span><a href="/parts/' + pynchon.parts.Parts.SanitizedPartNames[counter + 1] + '/" title="' + pynchon.parts.Parts.FormattedPartNames[counter + 1] + '">' + pynchon.parts.Parts.FormattedPartNames[counter + 1] + '</a>:'
            
            for i in part:
                ret = ret + ' [<a href="/episodes/' + pynchon.parts.Parts.SanitizedPartNames[counter + 1] + '/synopsis/episode_' + str(i) + '/" title="Synopsis of ' + pynchon.parts.Parts.FormattedPartNames[counter + 1] + ' Episode ' + str(i) + '">' + str(i) + '</a>],'


            ret = ret[0:len(ret) - 1]
            
            ret = ret + '<br/></span></p>'

{% endhighlight %}

<p>Anyway, the latest commit replaces that mess with the following view:</p>

{% highlight python %}
episodes_used = {}
presentation = []

for charsepinfo in charsinepisodes:
	if not charsepinfo.episode.part in episodes_used:
		episodes_used[charsepinfo.episode.part] = []
	episodes_used[charsepinfo.episode.part].append(charsepinfo.episode)
    {% endhighlight %}


<p>The models have now also been updated in the move towards abstraction from its original Pynchon-specific context. See the <a href="http://code.google.com/p/rockaby/source/detail?r=54a0f9af87f4b0b9003d4278b071d5c385b4b755">latest commit</a> for details.</p>