---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2013/07/07/evaluating-the-open-access-software-toolchain
categories:
- Publishing Technology
- Open Access
comments: []
date: 2013-07-07 19:39:48 +0200
date_gmt: 2013-07-07 18:39:48 +0200
doi: https://doi.org/10.59348/1qjzt-kfe68
roguescholar: https://rogue-scholar.org/records/yqzz2-69y16
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mgofozx2a
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- Technology
- OA
title: Evaluating the Open Access software toolchain
wordpress_id: 2737
wordpress_url: https://www.martineve.com/?p=2737
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mgofozx2a"
kcworks: https://works.hcommons.org/records/43622-3bd12
references:
- https://github.com/NateWr # Nate Wright GitHub profile
- http://www.ambraproject.org/ # Ambra open access publishing platform
- https://www.openlibhums.org # Open Library of Humanities website
- https://github.com/MartinPaulEve/meTypeset # meTypeset Word-to-NLM typesetting tool
- https://github.com/MartinPaulEve/MEXMLGalley/ # meXmlGalley NLM galley generation tool
- http://www.alluvium-journal.org # Alluvium online literary journal
---

<p>I received an interesting email this week from <a href="https://github.com/NateWr">Nate Wright</a>, who posed the following questions:</p>
<blockquote><p>I'm a web developer interested in contributing to a low-cost, open-source solution for online academic publishing. Prompted by a conversation with a former lecturer of mine, I've spent some time investigating the various open-source or low-cost options for digital journal publication (OJS, Scholastica, Annotum, Faculty, and the collection of tools being developed by the team at eLife).</p>
<p>It looks like OJS is the only open-source platform out there which can provide end-to-end capabilities for running a journal. In my own experience, though, I've grown wary of niche CMS's, which lack a large body of tools and community support to help inexperienced site admins easily customise and extend their website. Even fairly large and well-maintained CMS's, like Silverstripe, really suffer from the small size of their community developing plugins and themes. OJS seems pretty tightly bound to traditional publishing cycles as well, which will limit its utility as academic publishing transitions to new models. Speaking purely from the perspective of a mainstream web developer, if I was advising someone setting up a journal now, I would tell them they were taking a risk by committing to OJS. It's not clear how a successful journal website could mature on the platform over time and whether or not data would be portable if (when) a better solution arises in the future.</p>
<p>Both Scholastica and Faculty look like promising, affordable, easy-to-use end-to-end platforms. I'm sure they'll offer a workable solution for many small-scale journals even though they're proprietary.</p>
<p>But what I'm interested in contributing to is an open-source solution, built on a proven platform such as Wordpress or Drupal, which will ensure that content is "future-safe" and easy to customise, extend and adapt as academic publishing conventions change. These platforms are also supported by some of the cheapest hosting and design shops out there -- an unfortunate reality given the low budgets for open access journals in the humanities and social sciences.</p>
<p>This leaves Annotum for Wordpress. It looks like it has admirably managed to integrate some basic features -- JATS XML output, citation management and basic peer review. This is probably where I should put my efforts. But it was funded by Google so that Knol users could easily transfer their data. That's led the Annotum project to build everything into a bloated theme rather than modular plugins. It makes sense for their purposes, but it raises some concerns about the sustainability of the project.</p>
<p>Perhaps I'm being overly picky. But as a web developer I've come to feel that foundations really matter, because the web changes quickly and all-in-one tools can rarely keep up unless an organisation can afford regular, expensive development costs.</p>
<p>In order to make good choices about where I put my limited time, I'd like to better understand the core functionality needed to run a journal, and the priorities behind the toolsets that are needed. I was hoping you could help me by addressing a few questions. What are the tools you need to run a journal? Which tools need to be integrated with your online publishing platform? Which could be externalised to tools which are not tied into a particular publishing platform? What tools are you already using -- open-source or otherwise -- to meet your needs?</p></blockquote>
<p>I asked Nate if he'd mind if I replied publicly to this in a blog post because, quite frankly, this issue is important:</p>
<ul>
<li>Although we always go by the aphorism that the social problems are the ones that need fixing, we cannot neglect the technological</li>
<li>If we do not build and maintain an open toolset, we cannot rely on the arguments derived from the free software movement for ethical imperatives to OA</li>
<li>If we do not build and maintain an open toolset, we will be beholden to proprietary lock-in and outside determination of workflow (which drives peer review)</li>
</ul>
<p>So, let me sum up my position. OJS is an amazing piece of kit, but the criticism's above are entirely valid. OJS was ahead of the curve and developed along traditional workflow lines. I'm sure that PKP realise this. After all, Open Monograph Press has a far more flexible workflow (and awesomely sleek design!) Now, OJS is problematic for these reasons, but it's also amazing for running a journal and very much open to external contributions. It's GPL licensed, stored on GitHub and generally maintained by nice people who are willing to spend their time guiding new developers through their first commit.</p>
<p>Annotum does, indeed, look as though it's doing some amazing things, but the elephant in the room is <a href="http://www.ambraproject.org/">Ambra</a>, PLOS' system. Now, I've heard mixed reports on Ambra ("is it overkill?" etc) and I can't comment on their policy towards collaborative development, but it is an Apache licensed project with a comprehensive Wiki and Trac system in place. Definitely worth exploring.</p>
<p><a href="https://www.openlibhums.org">Our</a> submission platform is going to take Ambra as a base, most likely. Typesetting in NLM format will be done through our (very) in-development tool, <a href="https://github.com/MartinPaulEve/meTypeset">meTypeset</a>. This is AGPL v2 licensed and I'd welcome contributions; it's a basic attempt to start towards the functionality of extyles. The basic premise is that, through a series of XSLT stylesheets and python-driven regex parsing, it converts a Word/OpenOffice document into valid NLM/JATS XML. At present I also have a very rudimentary <a href="https://github.com/MartinPaulEve/meTypeset/tree/master/citeParse/meCite">citation parsing engine</a> in the works, also, as part of that project.</p>
<p>For my current layout generation, I use another in-house (but GPLed) tool, <a href="https://github.com/MartinPaulEve/MEXMLGalley/">meXmlGalley</a>. This is derived from OJS' (aborted?) attempt to integrate NLM. I revived the project and got OJS to drive FOP once more, adapted the stylesheet to give palatable output and have been tweaking the layout since. However, I don't tend to drive it via OJS now (even on OJS-run journals), I run the bash script to produce the PDF and HTML galleys and just upload them. This saves the potential instability of using PHP to launch command line tools to re-generate the PDF on the fly.</p>
<p>In any case, let me sum up what I do:</p>
<ul>
<li>Use OJS for my small niche joural, <a href="https://www.pynchon.net">Orbit</a>, which does a good job of document handling</li>
<li>Use Wordpress, without Annotum, for the quasi-magazine/journal <a href="http://www.alluvium-journal.org">Alluvium</a>, which is great at looking good</li>
<li>Use my own tools, <a href="https://github.com/MartinPaulEve/meTypeset">meTypeset</a> and <a href="https://github.com/MartinPaulEve/MEXMLGalley/">meXmlGalley</a> for typesetting and layout editing, currently with too much human intervention</li>
<li>Use an Ambra testbed for experimentation</li>
</ul>
<p>Here's what needs to happen (and I'm working on it):</p>
<p>The formation of an Open Access Toolset Alliance. I've begun to coordinate a group of people interested in this. The idea would be that we discuss what we are doing and ensure that we don't replicate labour re-building the same tools. There is scope for a variety of approaches, but if we are going to re-build the publishing toolchain in fully open software, we need to work in greater dialogue than the closed silos that can sometimes develop. There'll be a website forthcoming on this, but if people are interested, please <a href="mailto:martin.eve@openlibhums.org">email me</a>.</p>
<p>I think, to respond to Nate's specific question, that if we want tools that can plug in to any architecture, then we need to start working out where we have tied things too closely to our platforms, come up with standard interface formats and begin abstracting the functionality. In fact, that might be the best approach: find a project that has locked in the functionality and to then liberate it might be a good first step.</p>