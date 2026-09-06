---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2012/07/13/starting-an-open-access-journal-a-step-by-step-guide-part-4
categories:
- Open Access
- Publishing Technology
comments: []
date: 2012-07-13 10:41:45 +0200
date_gmt: 2012-07-13 10:41:45 +0200
doi: https://doi.org/10.59348/3vadh-txt21
roguescholar: https://rogue-scholar.org/records/9ddq5-wnp87
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mi7m3xh2r
image:
  feature: oa.png
layout: post
ogImage: images/oa.png
published: true
status: publish
tags: []
title: 'Starting an Open Access Journal: a step-by-step guide part 4'
wordpress_id: 2209
wordpress_url: https://eve.gd/?p=2209
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mi7m3xh2r"
kcworks: https://works.hcommons.org/records/60kr4-qgk16
references:
- title: 'Excursions: An interdisciplinary journal'
  type: WebSite
  url: http://www.excursions-journal.org.uk
- http://pkp.sfu.ca/support/forum/viewtopic.php?f=9&t=6817 # PKP forum thread on adding DOI display to OJS
- title: Journal Publishing Tag Set Tag Library version 2.3
  type: TechArticle
  url: http://dtd.nlm.nih.gov/publishing/tag-library/2.3/index.html
- title: A plugin for Open Journal Systems to generate PDF galleys from XML
  type: SoftwareSourceCode
  url: https://github.com/MartinPaulEve/MEXMLGalley
  isPartOf:
    name: GitHub
    type: WebSite
- title: MathML Namespace
  type: WebPage
  url: http://www.w3.org/1998/Math/MathML
  isPartOf:
    name: W3C
    type: WebSite
- title: XLink namespace
  type: WebPage
  url: http://www.w3.org/1999/xlink
  isPartOf:
    name: W3C
    type: WebSite
- http://www.w3.org/2001/XMLSchema-instance # W3C XML Schema instance namespace URI
- title: Deed - Attribution 2.0 Generic
  type: WebPage
  url: http://creativecommons.org/licenses/by/2.0/
  isPartOf:
    name: Creative Commons
    type: WebSite
- http://www.nytimes.com/1998/03/04/books/pynchon-s-letters-nudge-his-mask.html?pagewanted=all # NYT article Pynchon letters nudge his mask
---

<p>Following on from <a href="https://eve.gd/2012/07/10/starting-an-open-access-journal-a-step-by-step-guide-part-1/">part 1</a>, <a href="https://eve.gd/2012/07/11/starting-an-open-access-journal-a-step-by-step-guide-part-2/">part 2</a> and <a href="https://eve.gd/2012/07/12/starting-an-open-access-journal-a-step-by-step-guide-part-3/">part 3</a>, this is the third in a series of posts designed to get a new journal off the ground.</p>
<p><img src="https://eve.gd/wp-content/uploads/2012/07/file0001289799291-1024x768.jpg" alt="Keyboard" title="Keyboard" style="width:750px;" class="alignnone size-large wp-image-2211" /></p>
<h4>Copyediting and Proofreading</h4>
<p>When I started out work on <a href="http://www.excursions-journal.org.uk">Excursions journal</a> almost three years ago, I didn't know the difference between copyediting and proofreading. In short: copy editing is the process of bringing a piece in line with house style. It should aim to eradicate all grammatical, spelling and stylistic anomalies. The typesetting phase then converts the piece into the version it will appear in the final issue (a galley). The proofreading phase should, technically, only look for problems in the transcription from the copyedited version to the galley. Inevitably, though, things get missed, so it becomes an iterative process between typesetting and proofreading.</p>
<p>There are two routes that I'm going to present to you here for typesetting an article. The one you select will depend upon your technical competence, but also the effort you're willing to invest to get things right.</p>
<p>The less brilliant of the two options is this: simply export, via Word, your copyedited version into a PDF. Why is this not so great?:</p>
<ul>
<li>Not everybody likes PDFs. They should have a choice of a PDF or other formats, such as XHTML</li>
<li>The PDF is unlikely to contain the correct metadata</li>
<li>It becomes difficult to maintain stylistic consistency between articles</li>
</ul>
<p>However, if you do want to go down this route, it's not the end of the world and will still allow people to read your scholarship.</p>
<p><b>Typesetting Articles</b></p>
<p>Whether you're using the Word to PDF route, or the system I'm about to describe, there is a slight "Gotcha!" that you'll have to avoid. At the time of writing, OJS is not currently entirely ready to comply with CrossRef's terms and conditions for DOI display. To fix this, you'll need to edit the file article.tpl within your OJS installation's templates/article/ to <a href="http://pkp.sfu.ca/support/forum/viewtopic.php?f=9&t=6817">include the following line</a> beneath the abstract:</p>

{% highlight php %}
{if $article->getDOI()}<div id="doi">doi:&nbsp;<a href="http://dx.doi.org/{$article->getDOI()|escape}">{$article->getDOI()|escape}</a></div>{/if}
{% endhighlight %}

<p>This will enable you to see the DOI number on the landing page of the article (the abstract view). So, before you convert to PDF, or typeset in the more complex way that I'm about to describe, be sure to visit the preview of the article, grab the DOI number, and embed it somewhere near the top of the article. This will allow systems such as <a href="https://eve.gd/2012/06/06/metadata-handling-for-open-access-journal-pdfs/">Zotero to automatically get the metadata</a> for the article.</p>
<p>So, what's the more complex way of typesetting an article? The <a href="http://dtd.nlm.nih.gov/publishing/tag-library/2.3/index.html">NLM provides a tagset</a> specifically designed to enable XML typesetting of journal articles. I have spent some time, in the past few months, reworking an old, barely maintained plugin for OJS, that will enable you to typeset your articles in XML and then create PDF and HTML outputs from the same single document. The tools I have developed are open source and licensed under the GPL, so you can use and modify them (for no charge) so long as you stick to the license. They're available at: <a href="https://github.com/MartinPaulEve/MEXMLGalley">my github page</a>. This is why I cannot agree with people such as Scholastica who <a href="http://blog.scholasticahq.com/post/26974943233/open-access-open-source">do not release their entire toolchain</a>. Without the tools, a widespread transformation is not likely to happen.</p>
<p>The tools run on Linux and I have no plans to rewrite them for Windows, so I'm afraid you'll need some geek knowledge to use them. As I stipulated in the pre-requisites in <a href="https://eve.gd/2012/07/10/starting-an-open-access-journal-a-step-by-step-guide-part-1/">part 1</a>, I've assumed a humanities readership and not all of our needs were met by the NLM stylesheet. I haven't, I'm afraid, always implemented these in the most standards-friendly or beautiful way, but I hope to keep working on it so that, eventually, the whole thing is done properly. At present, there are a few workarounds.</p>
<p>So, here's what an article looks like typeset in the XML format:</p>

{% highlight xml %}
<?xml version="1.0" ?>
<article
dtd-version="3.0" xml:lang="en" 
xmlns:mml="http://www.w3.org/1998/Math/MathML" 
xmlns:xlink="http://www.w3.org/1999/xlink" 
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<!-- SYSTEM:  Archiving and Interchange DTD Suite    -->
<!-- Updated July 2007 An archival journal article with minimal 
Front Matter, a Table, and Citations for testing         -->
<!-- =============== Front Matter (Metadata) =========== -->
<front>
<journal-meta>
<journal-id>Orbit: Writing Around Pynchon</journal-id>
<issn>2044-4095</issn>
<publisher><publisher-name>Orbit: Writing Around Pynchon</publisher-name></publisher>
<uri>https://www.pynchon.net</uri>
</journal-meta>
<article-meta>
<article-id pub-id-type="doi">10.7766/orbit.v1.1.33</article-id>
<title-group>
<article-title>The Two <italic>V.</italic>s of Thomas Pynchon, or From Lippincott to Jonathan Cape and Beyond</article-title>

<abstract><p>Two versions of <italic>V.</italic> were issued in 1963, one in the U.S. and one in England, because errors that had crept into the first American edition were found and corrected in time for the British edition's release. Pynchon would be able to get the corrections he had made for the British edition into the American paperback the following year. The fact that the first U.S. edition needed to be corrected was forgotten, and with the exception of those printed by Bantam, the U.S. paperback publisher, all other U.S. editions are reproductions of the uncorrected first American edition. This paper traces the editorial history of <italic>V.</italic> after its publication, detailing the differences between the corrected and uncorrected editions of the novel.</p></abstract>
</title-group>

<self-uri>https://www.pynchon.net/owap/article/view/33</self-uri>

<contrib-group>

<contrib contrib-type="author">
<name><surname>Rolls</surname>
<given-names>Albert</given-names>
</name>
<xref ref-type="aff">
</xref>
</contrib>
</contrib-group>

<aff>
        Independent Scholar
</aff>


<pub-date pub-type="pub">
        <year>2012</year>
      </pub-date>
      <volume>1</volume>
      <issue>1</issue>
      <permissions>
      <copyright-statement>Copyright &#x00A9; 2012, Albert Rolls</copyright-statement>
<license license-type="open-access" xlink:href="http://creativecommons.org/licenses/by/2.0/">
<license-p>This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.</license-p>
</license>
      </permissions>

</article-meta>
</front>
<!-- =============== Body Matter (Content) =========== -->
<body>
<p>When <italic>V.</italic> appeared in bookstores in March of 1963, Thomas Pynchon had already become displeased with the published text. It was not the first time he had found himself unhappy about the content of his novel. He had begun editing it less than two months after he had submitted the typescript to Lippincott in the summer of 1961, reworking the original ending by polishing "the dialogue which was pretty wretched and insert[ing] a new yarn whose only justification is that I like it."<fn-link id="xr1" href="fn1"><sup>1</sup></fn-link> That early rewriting was carried out before Corlies (Cork) Smith, Pynchon's editor at Lippincott, offered any suggestions for the text's improvement, suggestions that he had promised were forthcoming in an August 2 letter to Pynchon, the first piece of correspondence Smith sent the young author after the typescript of <italic>V.</italic> had been accepted. Pynchon, mostly without anyone's urging, would go on to revise the book, reorganizing and cutting the text during the spring of 1962 and then cutting more, "the equivalent of twelve pages of published text,"<fn-link id="xr2" href="fn2"><sup>2</sup></fn-link> in the fall, while the galleys were in the proofing stage. Pynchon's editorial work was still not complete. Although his review of the Advanced Reading Copy did not raise any alarms, as it is essentially "identical to the first edition,"<fn-link id="xr3" href="fn3"><sup>3</sup></fn-link> oversights during the editing and proofing processes later left him regretting his own imperfections. "About the time the first batch came off the presses,"<fn-link id="xr4" href="fn4"><sup>4</sup></fn-link> Pynchon found a number of errors — beyond the typos, the presence of which he discounted as excusable, although not without remarking that "they make gibberish out of otherwise respectable sentences" — and felt obliged to tweak the novel one last time.<fn-link id="xr5" href="fn5"><sup>5</sup></fn-link></p>
<p>Not everything with which he found fault was unequivocally wrong. An overly critical eye was in part the source, perhaps the foremost source, of his discontent, the earliest available evidence of which are comments he made in a March 9 letter to Faith Sale, a college friend who worked at Lippincott and took on some of the editorial responsibilities for <italic>V.</italic> after Smith left that publisher for a job with Viking.<fn-link id="xr6" href="fn6"><sup>6</sup></fn-link> The last mistake to which Pynchon, who was apparently responding to a remark Sale had made about errata in an earlier letter, draws Sale's attention involves his having "Esther snea[k] out with Rachel's raincoat on," because "Rachel is a size 3 at biggest (though I never do say how big E. is —  but it's still sloppy)." Pynchon then writes, "And on and on like that," suggesting that there are many similar problems that he would like to have cleared up.<fn-link id="xr7" href="fn7"><sup>7</sup></fn-link> Rachel, however, is not likely to be a size three, as she is, despite her small stature, described as "voluptuous" (22) when she is first introduced.<fn-link id="xr8" href="fn8"><sup>8</sup></fn-link> Her raincoat would seem, if anything, too short on Esther — assuming Esther is what would have been regarded as an averaged height woman in the mid-twentieth century. Rachel's high heels, after all, lift her to 5'1" (216),<fn-link id="xr9" href="fn9"><sup>9</sup></fn-link> meaning the raincoat could be for a woman taller than Rachel's 4'10" (34) and would be, at most, a few inches higher up Esther's leg than it was meant to be and not necessarily an ill fit at all.<fn-link id="xr10" href="fn10"><sup>10</sup></fn-link></p>
<p>The problem Pynchon had with putting Esther in Rachel's coat seems to be that he had never considered the possibility that Rachel's size might prevent Esther from properly fitting into it and became self-conscious about failing to make the details of the novel cohere. His fear that such was the case does go beyond his penchant for finding fault with his work.<fn-link id="xr11" href="fn11"><sup>11</sup></fn-link> The mistakes that "no writer with even half an idea of what he's doing would have made" concerned such issues as having Profane, Angel, and Geronimo at a bar until "Last Call" (149) and then proceeding, on the next page, to have them search the city until midnight; having Sidney arrive in Valletta in the winter but then writing "it's June" on the same page;<fn-link id="xr12" href="fn12"><sup>12</sup></fn-link> writing "two pages on . . . it's been 7 months since armistice," that is, in June, though it soon becomes winter again; and using Arabic <italic>gebel</italic> to mean <italic>desert</italic> when "it means mountain."</p>
<p>Pynchon, of course, wanted to correct the text, but because he had not seen the errors until after the first printing and Lippincott wasn't going to pulp a print run for editorial reasons, putting back the publication date yet again,<fn-link id="xr13" href="fn13"><sup>13</sup></fn-link> the best he could hope for was that future printings and editions, that is, the British edition, the Bantam paperback, and, if he knew about it as early as March 1963, the Modern Library edition, the rights for which had been secured by the end of the summer of 1963,<fn-link id="xr14" href="fn14"><sup>14</sup></fn-link> could be fixed. Correcting the British edition was not a problem. The British publisher Jonathan Cape had printed its own Advanced Reading Copy, and perhaps even galleys, and Pynchon had sent a letter discussing corrections for it, almost certainly pointing out the newly discovered problems, to Candida Donadio on March 4.<fn-link id="xr15" href="fn15"><sup>15</sup></fn-link> He also informed Lippincott, telling Stewart (Sandy) "Richardson about them all because Bantam bought it for paperback and the goofs ought to be cleared up before then."<fn-link id="xr16" href="fn16"><sup>16</sup></fn-link> The Lippincott hardcover, Pynchon must have hoped, would be the only edition that had not been cleaned up, and he even harbored the illusion that hardback reprints could be fixed as well, explaining to Sale at the end of June, "all I could do was write Richardson . . . and ask him to edit it [the mistake] out of any other printings there might be."<fn-link id="xr17" href="fn17"><sup>17</sup></fn-link></p>
<p>Lippincott never made the corrections for the three hardcover reprints, the last of which was issued in June 1963,<fn-link id="xr18" href="fn18"><sup>18</sup></fn-link> but the 1964 Bantam paperback was published in a corrected state, meaning either Richardson passed on the corrections or Pynchon informed Bantam of his post-publication edits as he had done with Jonathan Cape, whose edition also lacks the obvious errata found in the first American edition. Those with the edition of <italic>V.</italic> published by Lippincott find "'the city is only the desert — gebel — in disguise.' Gebel, Gebrail. Why should he not call himself by the desert's name? Why not?" (83),<fn-link id="xr19" href="fn19"><sup>19</sup></fn-link> whereas those in possession of a British or a Bantam edition, read at the same point in the novel, "the city is only the desert in disguise" (Cape, 83). On the following page of the Lippincott text, a sentence begins "But Gebrail/Gebel, the desert's angel, had . . ." while the corrected version reads, "But the desert's angel had . . ." (Cape, 84; Bantam, 72).<fn-link id="xr20" href="fn20"><sup>20</sup></fn-link> "They stayed to near Last Call," (149) in the Lippincott edition becomes "They stayed till 9:30 or 10" (Bantam, 135) — although the Jonathan Cape/Vintage edition contains a typo so that 9:30 is printed with a dot between 9 and 3 instead of a colon (149) — and in the first line of the next paragraph of the Cape and Bantam editions, "around midnight" (Lippincott, 149) has been removed. In the Epilogue, "[T]hough it was June" (456), as well as "After seven months" (458), is left out of the British and Bantam editions.</p>
<p>The most obvious problems, then, had been solved on both sides of the Atlantic by the spring of 1964, but the fact that the novel put out by Lippincott needed to be corrected was soon forgotten. The Modern Library <italic>V.</italic> (1966) was published in the original form, apparently having been printed using the film that was used to print the first edition or film produced from a copy of that edition. That does not mean corrections could not have been made. The Cape edition also seems to have been produced from a Lippincott copy, for besides using the same font and design as was used in the U.S. edition, the production staff at Cape did its best to align the British edition's pages to those in the American one, adding an extra line after the roman numeral v above the fifth section of Chapter 3 on page 81 so that page 85 and those that follow it in the chapter match the Lippincott edition, despite the changes made to pages 83 and 84, the latter of which begins and ends with the same words in both editions. However the various editions of <italic>V.</italic> were produced, of those that were printed from 1963 to 1966, only the British one and the Bantam mass market paperback contain Pynchon's final revisions, while the Lippincott and Modern Library texts contain the errors that contributed to Pynchon's condemning <italic>V.</italic> as "the worst novel in decades"<fn-link id="xr21" href="fn21"><sup>21</sup></fn-link> and referring to it as "that wretched novel of mine."<fn-link id="xr22" href="fn22"><sup>22</sup></fn-link></p>
<p>The issue, in any case, should have been settled, indeed had been settled in Britain and in the United States for about twenty years — between 1967 and 1986 — while the corrected Bantam edition was the only U.S. text being reproduced, but the problem resurfaced when Bantam lost the rights to reprint its edition and Lippincott's fiction catalogue was taken over by Harper and Row in the mid-1980s. The text of the first Perennial reprint — which also seems to have been produced using the original Lippincott edition, even though the chapter titles are centered rather than flushed to the left — followed the original American text to the letter and the later reprints continue to do so, with the exception of the introduction of new typos after two resettings, one in 1999 and the other in 2005. Meanwhile, the text that continues to be printed in Britain follows the Cape edition. Consequently, since 1986, the two versions of <italic>V.</italic> that were issued between 1963 and 1966 have been available to readers, and as in 1963, the corrected, near definitive edition,<fn-link id="xr23" href="fn23"><sup>23</sup></fn-link> has only been the British one, a Vintage paperback in its present manifestation, while those in the U.S who have been relying on the Perennial imprints, or the newly released Penguin e-book, have been reading an unauthorized text.</p>
</body>


<!-- =============== Back Matter (Ancillary) ======= -->
<back>
<fn-group>
	<fn><label><fn-link href="xr1" id="fn1">1</fn-link></label><p>Pynchon did not, he told Smith, significantly change the text, although he would later move the chapter now called the Epilogue to the end of the book. See Thomas Pynchon, letter to Corlies Smith, August 31, 1961 and Herman and Krafft.</p></fn>
	<fn><label><fn-link href="xr2" id="fn2">2</fn-link></label><p>For a comparison of the galleys and the published version of the book, see Herman, Krafft, and Krafft.</p></fn>
	<fn><label><fn-link href="xr3" id="fn3">3</fn-link></label><p>Herman, Krafft, and Krafft, p. 156.</p></fn>
	<fn><label><fn-link href="xr4" id="fn4">4</fn-link></label><p>Thomas Pynchon, letter to Faith and Kirkpatrick Sale, June 29, 1963.</p></fn>
	<fn><label><fn-link href="xr5" id="fn5">5</fn-link></label><p>I have avoided discussing typos in what follows unless they relate to passages that were reworked in the Jonathan Cape and Bantam editions.</p></fn>
	<fn><label><fn-link href="xr6" id="fn6">6</fn-link></label><p>Herman and Krafft, p. 3.</p></fn>
	<fn><label><fn-link href="xr7" id="fn7">7</fn-link></label><p>Thomas Pynchon, letter to Faith and Kirkpatrick Sale, March 9, 1963.</p></fn>
	<fn><label><fn-link href="xr8" id="fn8">8</fn-link></label><p>The passage was let stand. It is the only problem that Pynchon discusses that was not fixed, and all the passages that were corrected are related to errors that he told Sale about. His "on and on like that," therefore, must concern Esther-in-Rachel's-raincoat-type errors and suggests that, if he had had the freedom to do whatever he wanted after March 1963, he would have altered quite a few passages. The extent of the corrections that Pynchon had proposed but that were not made can only be a matter of conjecture until his letter to Donadio of March 4 — which should be more detailed than the one he sent to Sale as it concerns corrections for the British edition — at The Morgan Library is made available or the letter sent to Richardson comes to light. Unless otherwise noted, citations from <italic>V.</italic> are from the Lippincott edition (1963).</p></fn>
	<fn><label><fn-link href="xr9" id="fn9">9</fn-link></label><p>5'1" becomes "five foot one" (232, [2005]) while 4'10" becomes "four foot nine" (29, [2005]) in the most recent edition, which seems to have been proofread without reference to earlier copies, something  evinced, for example, by the introduction of italicized titles <italic>New York Times</italic> (429 [2005]) and <italic>L'Enlèvement des Vierges Chinoises — Rape of the Chinese Virgins</italic> (440 [2005]); of accents over "Orléanist" and "duc d'Orléans" (437 [2005]); and perhaps most significantly, of a period after the V (547 [2005]) that is placed under the text on the last page, a design feature in the original edition that now risks being read as part of the text.</p></fn>
	<fn><label><fn-link href="xr10" id="fn10">10</fn-link></label><p>The average height, which we must assume Esther had because the absence of any information about it suggests that it is unremarkable, would probably be below 5'5"; Jane Russell, for example, was considered tall at 5'7" (see <italic>Life</italic>). The problem is perhaps complicated by the next paragraph, in which Pynchon writes, "The girl [Esther] was always swiping things and then getting all kittenish when she was caught" (128). If "things" means clothes, especially garments other than coats or perhaps blouses, then revision is required, although the comment is vague enough to avoid raising any obvious questions. In any case, Esther, it could be argued, wouldn't steal clothes it was impossible for her to wear.</p></fn>
	<fn><label><fn-link href="xr11" id="fn11">11</fn-link></label><p>Pynchon's self-critical approach to his work is evident in his introduction to <italic>Slow Learner</italic> (1984); in letters he wrote to Donadio about <italic>The Crying of Lot 49</italic> in which he calls the novel "'a short story, but with gland trouble,' and hopes that [she] 'can unload it on some poor sucker'" (Gussow); and in a July 1, 1970 letter to Cork in which he worries "that the novel [which became <italic>Gravity's Rainbow</italic> (1973)] 'could be the biggest piece of shit since <italic>The Crying of Lot 49</italic>'" (see Howard).</p></fn>
	<fn><label><fn-link href="xr12" id="fn12">12</fn-link></label><p>Pynchon writes "in the same paragraph." See Thomas Pynchon, letter to Faith and Kirkpatrick Sale, Mar. 9, 1963.</p></fn>
	<fn><label><fn-link href="xr13" id="fn13">13</fn-link></label><p>Pynchon comments on Lippincott's pushing back the publication's date in a November 1962 letter. See Thomas Pynchon, letter to Faith and Kirkpatrick Sale, Nov. 23, 1962.</p></fn>
	<fn><label><fn-link href="xr14" id="fn14">14</fn-link></label><p>An internal memo dated Sept. 4, [1963] that is reprinted on the last page of <italic>Of a Fond Ghoul</italic> notes that both Bantam and the Modern Library have contracts to reprint the book.</p></fn>
	<fn><label><fn-link href="xr15" id="fn15">15</fn-link></label><p>See Gussow.</p></fn>
	<fn><label><fn-link href="xr16" id="fn16">16</fn-link></label><p>Thomas Pynchon, letter to Faith and Kirkpatrick Sale, Mar. 9, 1963.</p></fn>
	<fn><label><fn-link href="xr17" id="fn17">17</fn-link></label><p>Thomas Pynchon, letter to Faith and Kirkpatrick Sale, June 29, 1963. Pynchon is discussing the use of the word <italic>gebel</italic>. There is no mention of any of the other problems. Pynchon seems to be responding to a comment Sale made about the word when she forwarded reviews to him, the comments Pynchon made in March on the subject apparently having been forgotten.</p></fn>
	<fn><label><fn-link href="xr18" id="fn18">18</fn-link></label><p>Lippincott may have thought to do so if it had had the opportunity to release its own paperback edition, something it considered doing. See the September 4 memo that concludes <italic>Of A Fond Ghoul</italic> for the in-house discussion about printing a paperback edition, which Lippincott was unable to do because of the Modern Library contract, as a hand written note dated September 24 at the bottom of the letter states.</p></fn>
	<fn><label><fn-link href="xr19" id="fn19">19</fn-link></label><p>Patrick Hurley, in his dictionary of Pynchon character names, calls the <italic>gebel</italic>-passage "a rare instance of a clever, multifaceted name explained fully" (65), a fact that perhaps renders the passage valuable in that it illustrates something Pynchon tries to do even when naming marginal characters.</p></fn>
	<fn><label><fn-link href="xr20" id="fn20">20</fn-link></label><p>W. T. Lahmon, Jr. points out, without elaboration, "there are a few silent changes in the Bantam reprint–for instance, at the beginning of the Epilogue" (86 n4) and J. Kerry Grant notes that <italic>gebel</italic> has been "omitted from Bantam ed." (54) in <italic>A Companion to V.</italic> without attempting to explain the omission.</p></fn>
	<fn><label><fn-link href="xr21" id="fn21">21</fn-link></label><p>Thomas Pynchon, letter to Faith and Kirkpatrick Sale, Mar. 9, 1963.</p></fn>
	<fn><label><fn-link href="xr22" id="fn22">22</fn-link></label><p>Thomas Pynchon, letter to Faith and Kirkpatrick Sale, June 29, 1963.</p></fn>
	<fn><label><fn-link href="xr23" id="fn23">23</fn-link></label><p>A definitive edition would have typos cleared up.</p></fn>
</fn-group>

<ref-list>

  <ref id="R1">
    <label></label>
    <element-citation publication-type="book">
      <person-group person-group-type="author">
        <name>
          <surname>Grant</surname>
          <given-names>J. Kerry</given-names>
        </name>
      </person-group>
      <source>A Companion to <italic>V.</italic></source>
      <date>
	<year>2001</year>
      </date>
      <publisher-loc>Athens</publisher-loc>
      <publisher-name>University of Georgia Press</publisher-name>
    </element-citation>
  </ref>

  <ref id="R2">
    <label></label>
    <element-citation publication-type="journal">
      <person-group person-group-type="author">
        <name>
          <surname>Gussow</surname>
          <given-names>Mel</given-names>
        </name>
      </person-group>
      <date>
	<year>1998</year>
	<month>March</month>
	<day>04</day>
      </date>
      <article-title>"Pynchon's Letters Nudge His Mask"</article-title>
      <source>New York Times</source>
      <uri>http://www.nytimes.com/1998/03/04/books/pynchon-s-letters-nudge-his-mask.html?pagewanted=all</uri>
      <date-in-citation content-type="access-date"><year>accessed 2012-01-04</year></date-in-citation>
    </element-citation>
  </ref>

   <ref id="R3">
    <label></label>
    <element-citation publication-type="journal">
      <person-group person-group-type="author">
        <name>
          <surname>Herman</surname>
          <given-names>Luc</given-names>
        </name>
        <name>
          <surname>Krafft</surname>
          <given-names>John M</given-names>
        </name>
      </person-group>
      <article-title>"Fast Learner: The Typescript of Pynchon's <italic>V.</italic> at the Harry Ransom Center in Austin"</article-title>
      <source>Texas Studies in Literature and Language</source>
      <date>
	<season>Spring</season>
	<year>2007</year>
      </date>
      <issue>1</issue>
      <volume>49</volume>
      <fpage>1</fpage>
      <lpage>20</lpage>
      <pub-id pub-id-type="doi">10.1353/tsl.2007.0005</pub-id>
    </element-citation>
  </ref>

  <ref id="R4">
    <label></label>
    <element-citation publication-type="journal">
      <person-group person-group-type="author">
        <name>
          <surname>Herman</surname>
          <given-names>Luc</given-names>
        </name>
        <name>
          <surname>Krafft</surname>
          <given-names>John M</given-names>
        </name>
        <name>
          <surname>Krafft</surname>
          <given-names>Sharon B</given-names>
        </name>
      </person-group>
      <article-title>"Missing Link: The <italic>V.</italic> Galleys at the Morgan Library and the Harry Ransom Center"</article-title>
      <source>Variants</source>
      <date>
	<year>2008</year>
      </date>
      <volume>7</volume>
      <fpage>139</fpage>
      <lpage>157</lpage>
    </element-citation>
  </ref>

  <ref id="R5">
    <label></label>
    <mixed-citation publication-type="website">
      <person-group person-group-type="author">
        <name>
          <surname>Howard, Gerald.</surname>
        </name>
      </person-group>
	(<date>
	<year>2005</year>
      </date>).
      <article-title>"Pynchon from A to V"</article-title>.
      <source>Book Forum</source>.
      <uri>http://www.bookforum.com/archive/sum_05/pynchon.html</uri>,
      <date-in-citation content-type="access-date"><year>accessed 2012-04-23</year></date-in-citation>.
    </mixed-citation>
  </ref>

  <ref id="R6">
    <label></label>
    <element-citation publication-type="book">
      <person-group person-group-type="author">
        <name>
          <surname>Hurley</surname>
          <given-names>Patrick</given-names>
        </name>
      </person-group>
      <source>Pynchon Character Names: A Dictionary</source>
      <date>
	<year>2008</year>
      </date>
      <publisher-loc>Jefferson</publisher-loc>
      <publisher-name>McFarland</publisher-name>
    </element-citation>
  </ref>

  <ref id="R7">
    <label></label>
    <element-citation publication-type="journal">
      <article-title>"Jane Russell Can Be Seen Everywhere But in a Movie"</article-title>
      <source>Life</source>
      <date>
	<year>2008</year>
        <month>April</month>
        <day>13</day>
      </date>
      <fpage>8</fpage>
      <lpage>9, 11</lpage>
    </element-citation>
  </ref>

   <ref id="R8">
    <label></label>
    <element-citation publication-type="bookchapter">
      <person-group person-group-type="author">
        <name>
          <surname>Lahmon, Jr.</surname>
          <given-names>W.T.</given-names>
        </name>
      </person-group>
      <chapter-title>"Pentecost, Promiscuity, and Pynchon's <italic>V.</italic>:  From the Scaffold to the Impulsive"</chapter-title>
      <source>Mindful Pleasures</source>
	<person-group person-group-type="editor">
        <name>
          <surname>Levine</surname>
          <given-names>George</given-names>
        </name>
        <name>
          <surname>Leverenz</surname>
          <given-names>David</given-names>
        </name>
      </person-group>
      <date>
	<year>1976</year>
      </date>
      <publisher-loc>Boston</publisher-loc>
      <publisher-name>Little Brown</publisher-name>
      <fpage>69</fpage>
      <lpage>86</lpage>
    </element-citation>
  </ref>

  <ref id="R9">
    <label></label>
    <mixed-citation publication-type="letter">
      <person-group person-group-type="author">
        <name>
          <surname>Pynchon</surname>
        </name>
      </person-group>, Thomas.
      (<date>
	<year>1962</year>
	<month>, November</month>
	<day> 23</day>
      </date>).
      <article-title> Letter to Faith and Kirkpatrick Sale</article-title>.
      <location>Harry Ransom Humanities Research Center, The University of Texas at Austin</location>.
    </mixed-citation>
  </ref>

  <ref id="R10">
    <label></label>
    <mixed-citation publication-type="letter">
      <person-group person-group-type="author">
        <name>
          <surname>Pynchon</surname>
        </name>
      </person-group>, Thomas.
      (<date>
	<year>1963</year>
	<month>, March</month>
	<day> 09</day>
      </date>).
      <article-title> Letter to Faith and Kirkpatrick Sale</article-title>.
      <location>Harry Ransom Humanities Research Center, The University of Texas at Austin</location>.
    </mixed-citation>
  </ref>

  <ref id="R11">
    <label></label>
    <mixed-citation publication-type="letter">
      <person-group person-group-type="author">
        <name>
          <surname>Pynchon</surname>
        </name>
      </person-group>, Thomas.
      (<date>
	<year>1963</year>
	<month>, June</month>
	<day> 29</day>
      </date>).
      <article-title> Letter to Faith and Kirkpatrick Sale</article-title>.
      <location>Harry Ransom Humanities Research Center, The University of Texas at Austin</location>.
    </mixed-citation>
  </ref>

  <ref id="R12">
    <label></label>
    <element-citation publication-type="book">
      <person-group person-group-type="author">
        <name>
          <surname>Pynchon</surname>
          <given-names>Thomas</given-names>
        </name>
      </person-group>
      <source>Slow Learner</source>
      <date>
	<year>1984</year>
      </date>
      <publisher-loc>Boston</publisher-loc>
      <publisher-name>Little Brown</publisher-name>
    </element-citation>
  </ref>

  <ref id="R13">
    <label></label>
    <element-citation publication-type="book">
      <person-group person-group-type="author">
        <name>
          <surname>Pynchon</surname>
          <given-names>Thomas</given-names>
        </name>
      </person-group>
      <source>V.</source>
      <date>
	<year>1963</year>
      </date>
      <publisher-loc>Philadelphia</publisher-loc>
      <publisher-name>J. B. Lippincott</publisher-name>
    </element-citation>
  </ref>

  <ref id="R14">
    <label></label>
    <element-citation publication-type="book">
      <person-group person-group-type="author">
        <name>
          <surname>Pynchon</surname>
          <given-names>Thomas</given-names>
        </name>
      </person-group>
      <source>V.</source>
      <date>
	<year>1963</year>
      </date>
      <publisher-loc>London</publisher-loc>
      <publisher-name>Jonathan Cape</publisher-name>
    </element-citation>
  </ref>

  <ref id="R16">
    <label></label>
    <element-citation publication-type="book">
      <person-group person-group-type="author">
        <name>
          <surname>Pynchon</surname>
          <given-names>Thomas</given-names>
        </name>
      </person-group>
      <source>V.</source>
      <date>
	<year>1966</year>
      </date>
      <publisher-loc>New York</publisher-loc>
      <publisher-name>The Modern Library</publisher-name>
    </element-citation>
  </ref>

  <ref id="R15">
    <label></label>
    <element-citation publication-type="book">
      <person-group person-group-type="author">
        <name>
          <surname>Pynchon</surname>
          <given-names>Thomas</given-names>
        </name>
      </person-group>
      <source>V.</source>
      <date>
	<year>1964</year>
      </date>
      <publisher-loc>New York</publisher-loc>
      <publisher-name>Bantam</publisher-name>
    </element-citation>
  </ref>

  <ref id="R18">
    <label></label>
    <element-citation publication-type="book">
      <person-group person-group-type="author">
        <name>
          <surname>Pynchon</surname>
          <given-names>Thomas</given-names>
        </name>
      </person-group>
      <source>V.</source>
      <date>
	<year>1986</year>
      </date>
      <publisher-loc>New York</publisher-loc>
      <publisher-name>Perennial Library</publisher-name>
    </element-citation>
  </ref>


  <ref id="R17">
    <label></label>
    <element-citation publication-type="book">
      <person-group person-group-type="author">
        <name>
          <surname>Pynchon</surname>
          <given-names>Thomas</given-names>
        </name>
      </person-group>
      <source>V.</source>
      <date>
	<year>1995</year>
      </date>
      <publisher-loc>London</publisher-loc>
      <publisher-name>Vintage</publisher-name>
    </element-citation>
  </ref>

  <ref id="R19">
    <label></label>
    <element-citation publication-type="book">
      <person-group person-group-type="author">
        <name>
          <surname>Pynchon</surname>
          <given-names>Thomas</given-names>
        </name>
      </person-group>
      <source>V.</source>
      <date>
	<year>2005</year>
      </date>
      <publisher-loc>New York</publisher-loc>
      <publisher-name>Harper Perennial/Modern Classics</publisher-name>
    </element-citation>
  </ref>

  <ref id="B20">
    <label></label>
    <element-citation publication-type="book">
      <person-group person-group-type="author">
        <name>
          <surname>Pynchon</surname>
          <given-names>Thomas</given-names>
        </name>
        <name>
          <surname>Smith</surname>
          <given-names>Corlies M</given-names>
        </name>
      </person-group>
      <source>Of a Fond Ghoul: Being the Correspondence between Corlies M. Smith and Thomas Pynchon</source>
      <year>1990</year>
      <publisher-loc>New York</publisher-loc>
      <publisher-name>Blown Litter Press</publisher-name>
    </element-citation>
  </ref>
  
</ref-list>
</back>
</article>
{% endhighlight %}

<p>It looks pretty complex, but I assure you, it's not really so bad once you've got your head around it. If you've never seen an HTML document, then yes, this looks pretty daunting, but it's a simple tag system. &lt;p&gt; signifies the start of a paragraph, for instance. Each "opening tag" has a closing tag that looks like this: &lt;/p&gt;. Tags must always match.</p>
<p>Anyway, from there you can simply use the toolset to do the following (the first line is the command, the rest are the tool's output):</p>

{% highlight bash %}
tools/gengalleys.sh ./Eve.xml
INFO: Running PDF transform: /home/Mounts/TERA1/Documents/Programming/MEXMLGalleyPlugin/meXml/tools/genfop.sh ./Eve.xml
INFO: Running saxon transform: java -jar /home/Mounts/TERA1/Documents/Programming/MEXMLGalleyPlugin/meXml/tools/saxon9.jar -o /home/Mounts/TERA1/Documents/Programming/MEXMLGalleyPlugin/meXml/tools/../transform/debug/new.fo ./Eve.xml /home/Mounts/TERA1/Documents/Programming/MEXMLGalleyPlugin/meXml/tools/../transform/jpub/jpub3-APAcit-xslfo.xsl
INFO: Running FOP transform: fop -c /home/Mounts/TERA1/Documents/Programming/MEXMLGalleyPlugin/meXml/tools/../transform/fop.xconf /home/Mounts/TERA1/Documents/Programming/MEXMLGalleyPlugin/meXml/tools/../transform/debug/new.fo ./7-13-2012-Eve.pdf
Default page-height set to: 11in
Default page-width set to: 8.26in
The following feature isn't implemented by Apache FOP, yet: table-layout="auto" (on fo:table) (See position 1:4817)
The following feature isn't implemented by Apache FOP, yet: table-layout="auto" (on fo:table) (See position 5:2074)
The following feature isn't implemented by Apache FOP, yet: table-layout="auto" (on fo:table) (See position 5:2566)
INFO: Running HTML transform: /home/Mounts/TERA1/Documents/Programming/MEXMLGalleyPlugin/meXml/tools/genfop.sh ./Eve.xml
INFO: Running saxon transform: java -jar /home/Mounts/TERA1/Documents/Programming/MEXMLGalleyPlugin/meXml/tools/saxon9.jar -o ./7-13-2012-Eve.html.tmp ./Eve.xml /home/Mounts/TERA1/Documents/Programming/MEXMLGalleyPlugin/meXml/tools/../transform/jpub/jpub3-APAcit-html.xsl
Warning: at xsl:stylesheet of file:/home/Mounts/TERA1/Documents/Programming/MEXMLGalleyPlugin/meXml/transform/jpub/main/jpub3-html.xsl:
  Running an XSLT 1.0 stylesheet with an XSLT 2.0 processor
{% endhighlight %}

<p>This has created me a PDF document and its HTML counterpart, which I can then upload into OJS. There is also a plugin component for OJS that will allow you to generate the documents on the fly on the site, but I make no guarantee as to its stability. Also, if you change the template, previous documents will change, which is not good practice for an online journal, which should be immutable.</p>
<p>Whichever route you choose, it's not actually so hard to produce galleys. The second method is somewhat time consuming, but can be facilitated by using a copy and paste starter template through a tool such as http://xing.github.com/wysihtml5/ .</p>
<p>In the final (maybe!) part of this guide, I'll discuss what to do once you're ready to go, the things you need to do after launch and some strategies for the "difficult second issue".</p>
<p><a href="https://eve.gd/2012/07/13/starting-an-open-access-journal-a-step-by-step-guide-part-5/">Part 5 &gt;&gt;</a></p>