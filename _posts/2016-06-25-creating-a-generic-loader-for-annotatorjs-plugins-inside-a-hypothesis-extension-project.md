---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2016/06/25/creating-a-generic-loader-for-annotatorjs-plugins-inside-a-hypothesis-extension-project
date: 2016-06-25
doi: https://doi.org/10.59348/bhaqf-e5560
roguescholar: https://rogue-scholar.org/records/cq7yt-6yc85
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mbcddvo2u
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: Creating a generic loader for Annotator.js plugins inside a hypothes.is extension
  project
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mbcddvo2u"
categories:
- Programming
kcworks: https://works.hcommons.org/records/5n0j3-m3993
---

Part of the work for our grant to Birkbeck from the Andrew W. Mellon Foundation is to create a software project that uses the annotation backend of hypothes.is to allow others to translate scholarly works (and for a user base to then be able to view those translations). Essentially, we want the sentence keying tech. to key to foreign languages.

I'll be honest: so far, we've spent a _long_ time trying to learn and understand all the technologies used by hypothes.is so that our project can be a neat, self-contained, and non-repetitive codebase that draws in and overrides components of the annotation project. The hypothes.is project uses a dizzying number of technologies: pyramid, Annotator.js, coffeescript, javascript, jquery, python, AngularJS, node.js, browserify, postgres, nsqd, postgres, elasticsearch, redis, rabbitmq, and others. Because hypothes.is is a rapidly transforming project, we also have had to fix upon a certain version (and give instructions to revert the git tree of hypothes.is to the version we are using).

The challenge I had today, which I wanted to document here, was that I wanted to write-in a plugin for the hypothes.is-bundled version of annotator.js that would select a page, sentence-by-sentence, as part of our user interface. To achieve this, I spent quite some time today wrestling with the way that pyramid interacts with browserify in order to handle assets.yaml files spread across multiple projects.

The first thing I noted is that assets set to output in h: (that is, hypothes.is) prefixed namespace addresses seem to use the assets file from h, regardless of whether you have set additional depends in the assets file in annotran. I had, therefore, to copy + re-map the main.js loader file so that it was within annotran and so that my new, additional plugins were handled.

Secondly, plugins to hypothes.is's version/use of Annotator.js (such as TextSelection) are activated by a constructor call that takes place in sidebar.coffee. So, again, for now at least, I have duplicated sidebar.coffee and remapped its requires to a relative ("../")-type path. This affords us a space in which we can put constructor calls to various plugins that we might want to load and now gives a full environment for writing and loading plugins to Annotator from within annotran with minimal code duplication.

That said, it would be really nice if hypothes.is was a bit more, well, "hooky". What I mean by this is that although Pyramid allows asset overriding, it continues to cause us a whole world of pain every time we need to build in new features. The documentation on extending/re-using the project is also a work in progress at the moment, so we are just having to work things out as we go. I hope to continue to document this experience.