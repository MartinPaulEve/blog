---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2016/02/16/understanding-ofquals-inter-subject-comparability-rasch-model-tests-for-easyhard-subjects-at-gcse-and-a-level
categories:
- Higher Education
date: 2016-02-16
last_modified_at: 2026-09-06
doi: https://doi.org/10.59348/6p2nq-2tc18
roguescholar: https://rogue-scholar.org/records/9kb46-3aj48
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mbs6v5b2q
layout: post
tags:
- statistics
- education
title: Trying to understand Ofqual's inter-subject comparability Rasch model tests
  for easy/hard subjects at GCSE and A-Level
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mbs6v5b2q"
kcworks: https://works.hcommons.org/records/bezay-swz78
references:
- https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/486936/3-inter-subject-comparability-of-exam-standards-in-gcse-and-a-level.pdf # Ofqual inter-subject comparability statistical paper
- http://europepmc.org/abstract/med/23442327 # Europe PMC abstract on Rasch model method
- author: Chris Wheadon
  date: '2015-05-21'
  title: Dr Chris Wheadon (@nmmarking) on X
  type: BlogPosting
  url: https://twitter.com/nmmarking/status/601402361635074049
  isPartOf:
    name: X (formerly Twitter)
    type: WebSite
---

Last night I spent almost three hours reading [the full Ofqual statistical paper on subject comparability at school level in the UK](https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/486936/3-inter-subject-comparability-of-exam-standards-in-gcse-and-a-level.pdf). I am not a statistician (obviously) but I've set out below my working through of what they have presented and the underlying assumptions that they have made in case it's of interest to anyone. There could be some real errors in this, but it's the best I can do. I'd actually be really interested if a statistician wanted to have a look at this to let me know what I've got right. I'm currently re-building my basic statistical knowledge but I'm hardly there yet.

Here's what I *think* their model does, based on [the Ofqual paper](https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/486936/3-inter-subject-comparability-of-exam-standards-in-gcse-and-a-level.pdf), beyond the headlines:

* They've measured what they suppose to be underlying academic ability (called the "latent trait") across all fields by quantifying grades, creating a linear scale of this, then overlaying the actual score distributions from each discipline against the predicted model.
 
* Physics and maths are called "hard" here because there is a higher initial requisite "latent trait" requirement and because more "latent trait" is needed for each step distance (grade boundary) than in other disciplines. You have to have more of the "latent trait" across all disciplines to move up grade boundaries in these subjects and you also have to have an initial higher "latent trait" score to even get on the scale in the first place.

* Although critical thinking and general studies were ranked as hard (because they have a distribution that requires non-linear increase in the "latent trait") they also "under-fit" the model, because they have greater variance in the data than the STEM subjects that are also "hard". The statisticians interpret this to mean that these two subjects' exams, while hard, might be harder because of marking/data variance, not _necessarily_ because of an innate difficulty: "Over-fitting subjects are more discriminative than under-fitting subjects in differentiating students in terms of ability" (Page 14 of Ofqual paper).

* There are a number of underlying assumptions in their modelling. Most notably, the "latent trait" aspect can be questioned. The preceding point about discrimination, for instance, assumes that the latent trait is some common aspect of intelligence/ability that all subjects are measuring.

* The exams have changed considerably since the period in which this study was conducted. There is no indication, therefore, that what they have here modelled will hold if change any aspects of the exams, despite their historical analysis.

* How they define "hard" is derived by extracting a single score from multiple angles on their probabilistic modelling of the dataset (step distance and base requirement of latent trait).
 
* The A-Level modelling could be particularly suspect since their matrix is unlikely to have enough intersections between STEM and Arts. It might be statistically underpowered (invalid) but I can't tell.

* This analysis was based on an uncited collaboration between Q He (at Ofqual) and a statistician who runs a business that is building algorithmic marking techniques (Wheadon). I cannot obtain the paper itself that this based on, sadly, but this strikes me as interesting in itself.
 
## The longer version

Easy/hard is classified using a Rasch model test. This works by classifying subjects' (people's) latent "abilities" across a range and then measuring that idealised model back against the distribution of performance within a sub-group (the discipline). Because the term "subject" is confusing here, I'll revert to using "students" for people and "subject" for discipline, although in literature on the Rasch test that I can find it isn't always written like that and "subjects" are people.

So, first thing they do is to profile students: who are the students who rank most highly on a latent trait continuum (the "latent trait" is the mysterious thing that lets them fare well in exams)? How this was actually done is a little vague in the Ofqual paper (page 9), but basically they assigned numbers to grades and then arranged each student into a matrix with subjects for rows:

<table>
<tr><td></td><td>English</td><td>Maths</td><td>Y Subject</td></tr>
<tr><td>Ted</td><td>1</td><td>2</td><td></td></tr>
<tr><td>Emma</td><td>1</td><td>2</td><td></td></tr>
</table>

Page 6 of the study describes the extraction of these data from the national student database. Once you have thousands and thousands of these rows, you can essentially say: tell me how likely it is that someone with a 1 in English and a 2 in Maths is to have an X in Y based on the existing set (although you'll usually specify many more than 2 input parameter subjects). The higher the person is probabilistically predicted to be across all subjects defines his or her "latent trait" score.

But there is also this caveat about the "latent trait" in the Rasch test:

>"However, it has to be noted that, when the Rasch model is used to analyse such data, the latent trait is operationally defined by the set of exams included in the analysis. This makes it difficult to interpret clearly the latent trait implied. It is likely that such a trait would be dominated by the underlying constructs of the subjects that are highly correlated. As mentioned earlier, in interpreting the results from Rasch analysis of the GCSE exam data, Coe (2008) interpreted such a trait as the ‘general academic ability’ of the individual students."

In other words, they assume here that the latent trait is "general academic ability" and that this is what will mostly closely correlate between individuals as the underlying reason why people fare differently in different subject exams. This makes some sense from the logic of testing but it might make less sense in a broader social environment; is there a commonality? They take the reading that is favourable for their study; that there is a common "general intelligence" that is cross-comparable and the latent trait is singular. I think this could be a problem if there aren't comparable latent traits that distinguish cross-subject ability. They acknowledge this to some degree: "GCSEs in physical education, music, short course IT, drama, and art have infit statistics considerably higher than those for other subjects, and they fit the Rasch model less well".

The next step is to use the statistical test to look for anomalies in each bracket of latent ability by distribution and by starting level. In other words: are there subjects where when you order students by the latent trait score they don't achieve grade rises at the same rate? In such subjects you have to have more latent trait (assumed to be academic ability) to achieve a commensurate rise in grade when compared to other subjects. These subjects are called "hard" for that reason. There is another reason, though: this can be broken down by grade; as they note on page 20, it can be "easier" to get a grade G in English than in Geography, even though it's harder to get an A* in English compared to Geography. So some subjects require more "latent trait" to even get started on the scale and then some subjects require more "latent trait" between grades. It's a bit like taking a ruler (that they've derived from the overall student body and that is called "latent trait") and then used it to measure the distance between grades in subjects and also how far off the ground the subject was (at each grade level) to begin with.

This modelling will work better -- if at all -- at GCSE since you have enough overlapping students to model the gaps in the matrix (not every student takes every subject). It probably gets far harder to profile at A Level due to the relatively small overlapping cohorts between different subjects. This is acknowledged on page 9: "The model parameters can be estimated for all persons and items _as long as there is sufficient overlap between them in the score matrix_" (my emphasis).

The most major limitation of this model seems to be outlined on pages 12-13 of the document, notably that there must be a _unidimensional_ relationship between ability and the examination. It must be that students didn't do well at an exam because they are weak and it must be that it was the _same reason_ that they didn't do well across subjects. If anything else interferes, then the Rasch test is invalid. This is tested by looking for "residuals"; calculating the Rasch probability and correlating with the actual outcome. If it's out by a factor of 2 or more then the measurement isn't valid for that student. So they are excluded. (Is that a valid approach or does it show that the model makes assumptions that don't hold in the real world?) They found that many students in the "U" band had residuals outside of the allowed bracket and so excluded that entire band from the study, setting "G" as the lower band.

BUT, there's another underlying thing going on here that's actually quite important. The Rasch test is based on evaluating at the QUESTION level for right/wrong questions (this is called a dichotomous set); not originally for the analysis of tiered bands that are grades across subjects (called a polytomous set). So, in this case, they've had to devise a way of applying a dichotomous Rasch test to a polytomous set.

While there are methods for doing this in long-standing software, like the application called WINSTEPS that they use, I think they used [this paper as the basis for the method](http://europepmc.org/abstract/med/23442327). I haven't got a copy because it seems the journal is print only(!) and may even have stopped publishing. Nonetheless, the article seems to do what is needed and it is co-authored by a member of Ofqual and a researcher called Chris Wheadon. Wheadon runs a company called "No More Marking" that aims to introduce algorithmic comparative judgement processes instead of marking. I think that he was previously a researcher at AQA. Anyway, this paper is not cited in the Ofqual document but [Wheadon confirmed on Twitter](https://twitter.com/nmmarking/status/601402361635074049) that he worked with Ofqual on the background to their study on Twitter. The document from Ofqual is titled "checked by QH", which is Q He -- the co-author of the Wheadon paper.

And that's where I've got to.