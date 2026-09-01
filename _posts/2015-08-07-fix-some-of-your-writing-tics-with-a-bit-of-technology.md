---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2015/08/07/fix-some-of-your-writing-tics-with-a-bit-of-technology
categories:
- Programming
- Academia
date: 2015-08-07
doi: https://doi.org/10.59348/w3z9z-97p33
roguescholar: https://rogue-scholar.org/records/9er3c-xvm60
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mce7dpe2n
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
tags:
- regex
- programming
- writing
title: Fix some of your writing tics with a bit of technology
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mce7dpe2n"
---

Everyone, when they are writing, can find themselves falling into bad habits. This is because, as my friend Liz Sage pointed out to me, when you are writing, you're trying to express thought. It's a writerly activity for you, the author, not thinking wholly of the reader. Examples of things that I do include repeating the same word in a sentence and using split infinitives. (I don't think there's actually much wrong with split infinitives in most cases. Academic editors probably will, though.)

There are two regular expressions that I use in my word processor to help with this. A "[regular expression](https://en.wikipedia.org/wiki/Regular_expression)" is "a sequence of characters that define a search pattern, mainly for use in pattern matching with strings, or string matching". In other words, the regex "[Mm]artin" would match "Martin" or "martin" in a case-sensitive environment. Most word processors have a way that you can enabled searches to use regular expressions. This is handy, as I'll show.

Finding repeated words within a sentence is easy with regex. Use:

    (\s\w+)\b[^\.]*\1\b

This searches for words with a boundary that are repeated before we encounter a full stop. It won't fix it for you, but it will show you where this is occurring. Of course, you will get some false positives, like multiple uses of "in" or "that" within a sentence.

Likewise, finding split infinitives (working on the logic that the adverb will usually end in "ly") can be achieved by using:

    to\s[^\s\.]+ly

This will find some instances that are not split infinitives ("linked to family records", for instance), but will probably hit more than it misses.

Edit: I've tested these in LibreOffice on Linux Mint. Some users have reported difficulties using them in Word for Mac.