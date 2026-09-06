---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2023/10/12/self-referential-language-counting
date: 2023-10-12
last_modified_at: 2026-09-06
doi: https://doi.org/10.59348/sf2b0-q3k31
roguescholar: https://rogue-scholar.org/records/96yqy-gjs90
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lxjbfpu2h
image:
  feature: header_words.png
layout: post
ogImage: images/header_words.png
title: Self-referential language counting (I learned another word today bringing my
  total to fourteen words and twenty letters)
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lxjbfpu2h"
categories:
- Programming
kcworks: https://works.hcommons.org/records/nsz9y-btv63
references:
- title: '2839: Language Acquisition'
  type: WebPage
  url: https://www.explainxkcd.com/wiki/index.php/2839:_Language_Acquisition
  isPartOf:
    name: explain xkcd
    type: WebSite
---

A [recent XKCD](https://www.explainxkcd.com/wiki/index.php/2839:_Language_Acquisition) caused some amusement: "Vocabulary update: I learned another word today, bringing my total to twelve".

We wondered whether there might be possible formulations of this joke that also contained the unique character count, so I wrote the following python script:


	import num2word
	import numpy

	def find_self_reference():
	    sentence = "I learned another word today bringing my total to {0} words and {1} letters"
	    words = 12

	    for i in range(0, 1000):
	        num_word = num2word.word(i)
	        final_words = words + numpy.char.count(num_word, " ") + 1
	        final_num_words = (
	            int(final_words)
	            + int(numpy.char.count(num2word.word(int(final_words)), " "))
	            + 1
	        )

	        sentence_sub = sentence.format(num2word.word(final_num_words), num_word)
	        characters = len(set(sentence_sub.replace(" ", "")))

	        print(f"Needed {characters} characters but got {i}.")

	        if characters == i:
	            print(sentence_sub)
	            return


This gives us the following results:

* I learned another word today bringing my total to fourteen words and twenty letters

or

* Vocabulary update: I learned another word today bringing my total to seventeen words and twenty five letters

Good to have a hobby.