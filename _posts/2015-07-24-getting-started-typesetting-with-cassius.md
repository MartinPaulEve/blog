---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2015/07/24/getting-started-typesetting-with-cassius
categories:
- typesetting
- PDF
- HTML
date: 2015-07-24
doi: https://doi.org/10.59348/9vcxf-95h70
image:
  feature: geek.png
layout: post
ogImage: geek.png
published: true
tags:
- typesetting
- PDF
- HTML
title: Getting started typesetting with CaSSius
---

Over the past week I've done some of the initial development work on [CaSSius](https://github.com/MartinPaulEve/CaSSius), the portion of the typesetter for the [Open Library of Humanities](https://www.openlibhums.org) that produces PDF output. The idea here is that, as a publisher, you want to produce one document and then create HTML and PDF from that single source. CaSSius provides two ways to achieve this. The first is to create your HTML using CaSSius's structure and to apply CSS styles when you want web output and to use CaSSius to create a PDF from this. The second is to create Journal Article Tag Suite XML and use CaSSius's importer to create the XML for you.

In this brief getting started guide, I'll demonstrate both techniques.

#Getting CaSSius
CaSSius is a work in progress and to use it requires a familiarity with the command line. To get CaSSius you'll need a working install of [Git](https://git-scm.com/), so go install it (like CaSSius, Git is free software). To use import functions, you also need an install of python and java. When you've got git working, you can run:

     git clone https://github.com/MartinPaulEve/CaSSius.git

This will clone the CaSSius repository to your local computer to whatever directory you are in when you run the command.

#Basic HTML usage
CaSSius takes an HTML document and uses some CSS and Javascript wizardry to paginate the document so that, when you use the "print to PDF" function in your browser, you can create a PDF. As per CaSSius's README file, a basic document structure for CaSSius looks like this:

    <body>
        <div id="cassius-content">
          <h1 class="articletitle"></h1>
          <div class="authors"></div>
          <div class="affiliations"></div>


          <div class="abstract">
              <h2>Abstract</h2>
              <p>Your abstract content here.</p>
              <p>As many paragraphs as needed.</p>
              <p class="oa-info">&copy; 2015 Martin Paul Eve. This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited.</p>
          </div>

          <div class="main">
              <div class="section">
                  <h1>A section title</h1>
                  <p>A paragraph.</p>
              </div>

              <div class="section">
                  <h1>A section title</h1>
                  <p>A paragraph with a footnote.<a href="#fn1--fragment" id="xr1"><sup>1</sup></a></p>
              </div>

              <div class="notes">
                  <h1>Notes</h1>
                  <div class="footnote"><p><span class="generated"><a href="#xr1--fragment" id="fn1">1</a></span> Footnote content goes here.</p></div>
              </div>

              <div class="references">
                  <h1 class="ref-title">References</h1>
                  <div class="section ref-list">
                      <ul>
                          <li class="ref-content">Adorno, Theodor W., <i>Negative Dialectics</i>, trans. by E.B. Ashton (London: Routledge, 1973)</li>
                      </ul>
                  </div>
              </div>
          </div>
        </div>

        <article id="article"></article>

        <script type="text/cassius" id="cassius-metadata">
            <div id="cassius-metadata-block">
                <div id="cassius-title">Article typeset by CaSSius: heavyweight typesetting with lightweight technology</div>
                <div id="cassius-publication">CaSSius</div>
                <div id="cassius-authors">Martin Paul Eve</div>
                <div id="cassius-affiliations">Department of English and Humanities, School of Arts, Birkbeck, University of London, United Kingdom</div>
                <div id="cassius-doi">10.16995/olh.001</div>
                <div id="cassius-date">September 2015</div>
            </div>
        </script>
    </body>

This requires a little bit of unpacking, though, and works better with [a full example](/cassius/TwiggExample.html) (which is a book review written by George Twigg for my journal, _Orbit_). If you open this file in Firefox or Chrome, you should see a nicely paginated document which you can print to PDF with ease. However, this isn't a PDF. It's generated from the following HTML source:

    <html xmlns:xslt="http://xml.apache.org/xslt" xmlns="http://www.w3.org/1999/xhtml">
       <head>
          <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
          <meta charset="utf-8" />
          <meta http-equiv="X-UA-Compatible" content="IE=edge" />
          <title>Review of Simon Malpas and Andrew Taylor, <i>Thomas Pynchon</i> (Manchester University Press, 2013)
          </title>
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <link rel="stylesheet" href="https://raw.githubusercontent.com/MartinPaulEve/CaSSius/master/cassius/cassius.css" />
          <link rel="stylesheet" href="https://raw.githubusercontent.com/MartinPaulEve/CaSSius/master/cassius/cassius-content.css" />
          <script src="//use.typekit.net/ria4wnw.js"></script><script type="text/javascript">try{Typekit.load();}catch(e){}</script>
          <script type="text/javascript" src="https://raw.githubusercontent.com/MartinPaulEve/CaSSius/master/cassius/jquery.js"></script>
          <script type="text/javascript" src="https://raw.githubusercontent.com/MartinPaulEve/CaSSius/master/cassius/cassius.js"></script>
          <script src="https://raw.githubusercontent.com/MartinPaulEve/CaSSius/master/cassius/regions/css-regions-polyfill.min.js"></script></head>
       <body>
          <div id="cassius-content">
             <h1 class="articletitle"></h1>
             <div class="authors"></div>
             <div class="affiliations"></div>
             <div class="abstract">
                <h2>Abstract</h2>
                <p>Book review of Review of Simon Malpas and Andrew Taylor, <i>Thomas Pynchon</i> (Manchester University Press, 2013).
                </p>
                <p class="oa-info">Copyright © 2015, George William Twigg. This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited. The citation of this article must include: the name(s) of the authors, the name of the journal, the full URL of the article (in a hyperlinked format if distributed online) and the DOI number of the article.
                </p>
             </div>
             <div class="main">
                <div class="section">
                   <h1></h1>

                   <p>Simon Malpas and Andrew Taylor’s book is a welcome addition to Manchester University Press’s ‘Contemporary American and Canadian Writers’ series. Previous entries in the series include such complex, experimental authors as Paul Auster and Mark Z. Danielewski, amongst whom Pynchon is in good company.  Indeed, much of the book is devoted to discussing exactly how we may ‘read’ Pynchon’s difficult, allusive style.  The series editors’ foreword states that ‘[c]entral to the series is a concern that each book should argue a stimulating thesis, rather than provide an introductory survey’,<a class="footnote" href="#fn1--fragment" id="xr1"><sup>1</sup></a> and while we may wonder whether any book on Pynchon’s vast,  complex fictional world can truly be more than an ‘introduction’, Malpas and Taylor are indeed stimulating.  Their study provides a clear, lucid discussion of several key themes in Pynchon’s novels, chief amongst which are paranoia, the emancipatory power of fantasy and alternative modes of perception, and the ‘subjunctive potentiality’ (3) of spaces of resistance.  Malpas and Taylor’s analysis is always illuminating, and their analysis of space in particular ensures that their book is a significant contribution to the diffuse field of Pynchon scholarship.</p>

                   <p>Chapter One focuses on three of the stories published in <i>Slow Learner</i>. ‘Low-lands’ is placed in its historical and cultural context, with incisive readings of 1950s cultural critiques by figures such as David Riesman and C. Wright Mills, who argued that ‘[t]he success of American capitalism had led[…]to the occlusion of dissenting voices from debates about national identity’ (14).  Characteristically of their book, Malpas and Taylor examine space, warning that the apparent promise in ‘Low-lands’ of ‘a renewed privatised space and a reconstituted individuality’ (15) may be illusory, as the story’s ending suggests.  ‘The Secret Integration’ is read in conjunction with Pynchon’s article ‘A Journey Into the Mind of Watts’, with the authors sensitively charting the disparities between white and black experiences of life, as well as the attempt of the story’s children, through their imagined black companion, to resist the racialising discourse of their parents. Malpas and Taylor state that ultimately ‘imaginative intent is obstructed by entropic reality’ (31), an observation that frequently crops up in their later discussions of attenuated resistance.  Entropy itself, and ‘Entropy’, is the next topic explored, with clear and concise summaries of the thought of those – Norbert Wiener and Henry Adams – who influenced Pynchon’s understanding of entropy as a concept.  Effectively contrasting Adams, who ‘applied the second law of thermodynamics to all processes and systems’ (35), with Wiener, whose conception of entropy allows for less than total pervasiveness, Malpas and Taylor identify in ‘Entropy’ ‘a contrapuntal alternation between a view of the world as rational and contained[…]and one that contains the possibilities of disruption and chance’ (37).  In its appreciation of space and resistance in <i>Slow Learner</i>, this chapter effectively introduces the key themes of Malpas and  Taylor’s book as a whole, and anticipates the extension of these concerns to Pynchon’s novels in its later chapters.</p>
                   
                   <p>Chapter Two concerns not <i>V.</i>, Pynchon’s next work, but <i>The Crying of Lot 49</i>. Malpas and Taylor’s introductory chapter seeks to justify this achronological sequence by stating that ‘<i>Slow Learner </i>and <i>The Crying of Lot 49</i>[…]are taken as concentrated embodiments of the theoretical and contextual obsessions of a long writing career, but are in no way to be regarded as templates against which Pynchon’s other work is to be measured’ (6).  The authors go to some trouble to explain their appropriation of <i>Lot 49 </i>as ‘emblematic of the complexities of Pynchon’s work’ (48), but the idea that any novel, no matter how brief, can be a ‘concentrated embodiment’ of Pynchon’s writing fails to quite convince, considering the significant variation in style and theme across his oeuvre.  Happily, Malpas and Taylor’s analysis of <i>Lot 49</i> is stimulating regardless of its placement in the book.  The novel is considered as a detective story, after Edward Mendelson’s influential essay (52), taking the novel’s lack of closure, despite its proliferation of clues for Oedipa the ‘detective’, as crucial.  The authors see the world of <i>Lot 49</i> as a matrix of competing interpretative strategies in which meaning is not an answer but a ‘medium’ (54).  For readers, characters and critics alike – Malpas and Taylor provide a précis of two fundamentally different essays on <i>Lot 49</i> in support of this argument<a class="footnote" href="#fn2--fragment" id="xr2"><sup>2</sup></a> –  the novel is a maelstrom of intertexts, plots and referentialities that can be interpreted almost <i>ad infinitum</i>.  This analysis of the novel usefully anticipates Malpas and Taylor’s examination of the  complex openness of texts such as <i>Against the Day </i>and <i>Gravity’s Rainbow</i>.</p>
                   
                   <p>Chapter Three looks at plotting in <i>V.</i>, both in the narrative and conspiratorial senses; as in <i>Lot 49</i>, ‘[t]he world produced by the novel’s plots[…]remain[s] just at the limits of what can be grasped’ (76).  Malpas and Taylor explore the contrast between the ‘chaotic and never fully engaged wandering of Profane’, and ‘the obsessively ordered “hot-house”’ of Stencil’s ‘plotting’ (75), asserting that they are more alike than some might realise; Stencil is barely more engaged with history than Profane, as thanks to his obsession with V. he ‘displays an attitude so obsessively focused on a single figure that all other events, even those involving the most extreme suffering and horror, appear only on the sidelines’ (79).  Malpas and Taylor share Stencil’s concern with V. (though not its intensity), looking at intertexts of V. and <i>V.</i> through a survey of previous discussions of the novel’s relation to modernism, from Maarten  van Delden’s conception of the novel as satirising modernist ideas of coherence and art’s autonomy (82-4) to John Dugdale’s presentation of <i>V.</i> as an interrogation of the ‘violence that lies beneath the “mystique” of the modernist  image’ (84). Moving from modernism to postmodernism via a Huyssen-inflected examination of Pynchon’s equal and often concomitant use of ‘high’ and ‘low’ art (86), Malpas and Taylor demonstrate how <i>V</i>.’s characters are ‘aware of their implication in a field of prior texts and contexts’ (88), going on to discuss the novel’s treatment of gender and bodily transformation, both of which disrupt the idea of the human as postmodernism does (89).  <i>V.</i> is shown to be a novel that, through its plots, dislocates both humanity and  the possibility of interpretation.</p>
                   
                   <p>Chapter Four looks at <i>Gravity’s Rainbow</i>, and how it, even more so than Pynchon’s previous works, ‘piles complexity upon complexity’ (100), by ‘putting at stake the very possibility of reading and by presenting interpretation as a mode of paranoia’ (101). Taking Brian McHale’s influential analysis of the novel as precluding any concrete meaning as their starting point, as well as the critical approaches from their previous three chapters, Malpas and Taylor explore the novel’s anti-foundationalism and its multiple modes and genres of representation (103).  Of particular interest is the chapter’s treatment of space, which becomes a central concern in the remainder of the study.  The Zone is seen as ‘an anarchic space of possibility and competition from which the new, post-war world will be born’ (107), but as always Malpas and Taylor stress that hope for the future, and the possibility of a space that will become truly resistant to capitalism and the preterition felt by virtually all the characters in the novel (113), is attenuated.  As the novel is one of pervasive preterition, the authors go on to emphasise, rightly, how the ‘elect’ are ‘present only as a paranoid projection of an undefinable and inaccessible “They”’ (113), parlaying this trenchant observation into a discussion of interpretation-as-paranoia, suggesting that this equivalence is so for both character and reader (115). This chapter, as with Malpas and Taylor’s other chapters on Pynchon’s longer, more complex novels, is profoundly concerned with the difficulty of interpretation and reading, and throughout their book the two handle their appreciation of these difficulties with aplomb, offering rich ways into the text in lieu of the possibility of a coherent ‘reading’.</p>
                   
                   <p>Chapter Five opens by asserting that <i>Vineland</i>, with its mimesis of governmental paranoia, has ‘accrued a renewed sense of significance’ (126) since 9/11 and the War on Terror.  Sadly there is no extended elaboration upon this interesting observation, which is a shame, particularly considering that Malpas and Taylor’s discussion of echoes of 9/11 in the chapter on <i>Against the Day</i> is done so well.  This is not to say, however, that the chapter’s exploration of government oppression, and resistance thereto, is not illuminating.  Against Alec McHoul and Ellen Friedman’s criticisms of <i>Vineland</i> as ‘nostalgic’, Malpas and Taylor write that ‘Pynchon is able to establish a complex series of contrasts and continuations that work to disabuse the reader of any sense that the book is trading in the easy comforts of nostalgia for an earlier, more authentic moment’ (128).  For them, <i>Vineland</i> simultaneously ‘expos[es] those spectral traces of an alternative identity that attempt to resist the rationalising logic of modernity’, and demonstrates ‘Pynchon’s interest in the gradual co-opting of the counterculture by the government and media alike’ (130).  As always in Pynchon, resistance exists more as potentiality than effective practice.  Through a reading of the naïve, idealistic efforts of 24fps, the deterritorialising and co-opting effect of television and the novel’s precarious spaces of resistance, Malpas and Taylor show that, unlike in <i>Gravity’s Rainbow</i>, ‘[e]lect and preterite are often on close speaking/trading terms’ (146). As such, the tendrils of government, more hands-on than the shadowy ‘They’ of the earlier novel, are everywhere, with the same result – spaces of resistance are only such interms of <i>potentiality</i>.</p>
                   
                   <p>Chapter Six, as one would expect from an examination of <i>Mason &amp; Dixon</i>, a novel about a pair of cartographers, is profoundly concerned with space.  According to Malpas and Taylor, ‘the line[…]inaugurates a wider meditation on the centrality of divisions and demarcations in the American national narrative, their persecutory effect and their usefulness in establishing forms of instructive difference’ (154).  The ideological effect of space – ‘the stabilising impetus of mapping’ (163) – is central to this chapter, as is resistance to the cartography of the elect by America’s geography and its peoples; in Pynchon’s depiction of the disenfranchised Native Americans, ‘the ethnic rationalisation of continental space that the Mason-Dixon Line inscribes is contested by an indigenous population with an alternative geographical sensibility’ (170).  This chapter, like the previous one, focuses on the ‘spectral traces’ of an alternative spatial and ideological sensibility, suggested by, for example, ‘a focus on magic and the supernatural, and[…]the playfulness of language itself’ (164).  The biggest strength of Malpas and Taylor’s book is the work it does to uncover the spatiality of Pynchon, and in its assessment of <i>Mason &amp; Dixon</i> it does so particularly strongly.</p>

                   <p>Chapter Seven covers <i>Against the Day</i>, Pynchon’s longest novel. Stating from the outset that any attempt at countermanding the disorientation and displacement felt by the reader is futile, the chapter posits that the book does not just explore historical anarchism, but is itself an example of ‘<i>aesthetic </i>anarchy’ (185).  As with <i>Gravity’s Rainbow</i>, the very difficulty of finding meaning in a complex Pynchonian novel is the subject of inquiry, and it is a fruitful way than ever) to ‘American history[…]as a repeated narrative of aspiration giving way to disappointment’ (186).  The totalising effect of the reductive perspectives of technology and capitalism is of importance, and once more Malpas and Taylor assert that ‘Pynchon’s preterite figures are characteristically resilient, ghostly spectres of a system that has exiled them but which cannot completely erase their traces’ (192).  The end of the chapter states,</p>
                   
                   <div class="blockquote">
                      <p>Our belief that the Chums[…]will remain immune from the forces of political tension can only be a tentative one. But it is a hope that is nevertheless reinforced by a novel that, through its structural extravagance as well as its political thematics, has the capacity to open readers’ eyes to the potential for alternative ways of seeing (207).</p>
                   </div>
                   
                   <p>The potentiality of resistance through new ways of ‘reading’ both literature and the world is most vividly covered in this chapter, which suggests that Pynchon’s longest, most complex novels, while challenging, also offer the reward of new meanings and interpretations which, while they may not carry political power, have a power of their own to discursively shape human experience.</p>

                   <p>The book’s conclusion takes Michiko Kakutani’s influential designation of <i>Inherent Vice</i> as ‘Pynchon Lite’ – a relatively straightforward shorter novel in the ‘recognisable generic form of private-eye fiction’ (212) – as its starting point.  Malpas and Taylor discuss the novel in terms of the concerns of their previous chapters, with the 1960s, California, literary form, resistance and paranoia being paramount.  The chapter is half the length of the previous ones, and <i>Inherent Vice</i> is compared with six other Pynchon novels, with the result being that each comparison lacks the depth of the excellent work of the rest of Malpas and Taylor’s book. Not quite ‘Criticism Lite’, but it is a shame that a novel so often slighted by reviewers as insubstantial should be itself subject to a relatively insubstantial critique.  However, this is not to detract from the coherent and lucid work of the book as whole, nor its importance to the field, particularly to Pynchon scholars interested in space.  Malpas and Taylor deliver on their editor’s promise of a ‘stimulating thesis’, and then some.</p>
                </div>
                
                <div class="notes">
                   <h1>Notes</h1>
                   <div class="footnote">
                      <p><span class="generated"><a href="#xr1--fragment" id="fn1">1</a></span>  Nahem Yousaf and Sharon Monteith, ‘Series Editors’ Foreword’, Simon Malpas and Andrew Taylor, <i>Thomas Pynchon</i> (Manchester University Press, 2013), vi.
                      </p>
                   </div>
                   <div class="footnote">
                      <p><span class="generated"><a href="#xr2--fragment" id="fn2">2</a></span>  Mendelson, Edward (ed.), <i>Pynchon: A Collection of Critical Essays</i>, (Englewood Cliffs, NJ: Prentice-Hall, 1978); Colin Nicholson and Randall Stevenson, ‘“Words You Never Wanted to Hear”: Fiction,
                         History and Narratology in <i>The Crying of Lot 49</i>’, <i>Pynchon Notes</i> 16 (1985), 89-109.
                      </p>
                   </div>
                </div>
                <div class="references">
                   <h1 class="ref-title">References</h1>
                   <div class="section ref-list">
                      <ul>
                         <li class="ref-content">Nicholson, Colin,  &amp; Stevenson, Randall, "‘Words You Never Wanted to Hear’: Fiction, History and Narratology in <i>The Crying of Lot 49</i>", <i>Pynchon Notes</i> [16], 1985, pp. 89 - 109
                         </li>
                         <li class="ref-content">Mendelson, Edward, 
                            "The Sacred, the Profane and <i>The Crying of Lot 49</i>", in Edward Mendelson (ed.), <i>Pynchon: A Collection of Critical Essays</i> (Englewood Cliffs, NJ: Prentice-Hall Inc, 1978), pp. 112 - 146
                         </li>
                         <li class="ref-content">Yousaf and Sharon Monteith, Nahem,  &amp; Monteith, Sharon, "Series Editors' Foreword", in Simon Malpas &amp; Andrew Taylor (eds.), <i>Thomas Pynchon</i> (Manchester: Manchester University Press, 2013)
                         </li>
                      </ul>
                   </div>
                </div>
             </div>
          </div>
          <article id="article"></article>

          <script type="text/cassius" id="cassius-metadata">
              <div id="cassius-metadata-block">
                  <div id="cassius-title">Review of Simon Malpas and Andrew Taylor, <i>Thomas Pynchon</i> (Manchester University Press, 2013)</div>
                  <div id="cassius-publication">Orbit: Writing Around Pynchon</div>
                  <div id="cassius-authors">George William Twigg</div>
                  <div id="cassius-affiliations">University of Exeter</div>
                  <div id="cassius-doi">10.7766/orbit.v1.2.128</div>
                  <div id="cassius-date">2015</div>
              </div>
          </script>
          </body>
    </html>

While this document should be fairly self-explanatory and give a better idea of how to go about creating more complex outputs, there is one aspect that I should highlight: footnotes and internal links. Footnotes need a little bit of work. They should be encoded as links ("a" elements) but the href attribute needs to have an extra "--fragment" appended to it (as do any links to internal named anchors). So, if an anchor is defined as id="xr1" then the corresponding href should point to "#xr1--fragment" Hence these two links point at each other:

    <a class="footnote" href="#fn2--fragment" id="xr2"><sup>2</sup></a>
    <a href="#xr2--fragment" id="fn2">2</a>

Fundamentally, though, this is how you can create a single HTML document that then builds a PDF for you.

#Conversion from JATS
However, I didn't actually craft the above document by hand. Instead, I ran the following command from inside the CaSSius directory:

    ./cassius-import/bin/cassius-import.py ./Twigg.xml ./Twigg.html

This requires you to have a copy of Twigg.xml also inside the directory, which you can [download here](/cassius/Twigg.xml). This is the automatic JATS conversion script and it will take the XML and let you produce a CaSSius document. It only handles basic JATS at the moment, but this is the underlying structure:

    <?xml version="1.0" encoding="UTF-8" ?>
    <!DOCTYPE article PUBLIC "-//NLM//DTD Journal Publishing DTD v3.0 20080202//EN" "http://dtd.nlm.nih.gov/publishing/3.0/journalpublishing3.dtd">
    <article>
       <front>
        <journal-meta>
          <journal-id>Orbit: Writing Around Pynchon</journal-id>
          <issn>2044-4095</issn>
          <publisher><publisher-name>Orbit: Writing Around Pynchon</publisher-name></publisher>
        </journal-meta>
        <article-meta>
          <article-id pub-id-type="doi">10.7766/orbit.v1.2.128</article-id>
          <title-group>
            <article-title>Review of Simon Malpas and Andrew Taylor, <italic>Thomas Pynchon</italic> (Manchester University Press, 2013)</article-title>
            
          </title-group>
          
          <contrib-group>
            
            <contrib contrib-type="author">
              <name><surname>Twigg</surname>
                <given-names>George William</given-names>
              </name>
              <xref ref-type="aff">
              </xref>
            </contrib>
          </contrib-group>
          
                <aff><institution>University of Exeter</institution></aff>
          
          
          <pub-date pub-type="pub">
            <year>2015</year>
          </pub-date>
          <volume>1</volume>
          <issue>1</issue>
          <permissions>
            <copyright-statement>Copyright &#x00A9; 2015, George William Twigg</copyright-statement>
            <license license-type="open-access" xlink:href="http://creativecommons.org/licenses/by/2.0/">
              <license-p>This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited. The citation of this article must include: the name(s) of the authors, the name of the journal, the full URL of the article (in a hyperlinked format if distributed online) and the DOI number of the article.</license-p>
            </license>
          </permissions>
          
          <self-uri>https://www.pynchon.net/owap/article/view/128</self-uri>
          <abstract><p>Book review of Review of Simon Malpas and Andrew Taylor, <italic>Thomas Pynchon</italic> (Manchester University Press, 2013).</p></abstract>
        </article-meta>
      </front>
      <body>
        <sec>
          <title/>
          <p>Simon Malpas and Andrew Taylor&#8217;s book is a welcome addition to Manchester University Press&#8217;s &#8216;Contemporary American and Canadian Writers&#8217; series. Previous entries in the series include such complex, experimental authors as Paul Auster and Mark Z. Danielewski, amongst whom Pynchon is in good company.  Indeed, much of the book is devoted to discussing exactly how we may &#8216;read&#8217; Pynchon&#8217;s difficult, allusive style.  The series editors&#8217; foreword states that &#8216;[c]entral to the series is a concern that each book should argue a stimulating thesis, rather than provide an introductory survey&#8217;,<xref ref-type="fn" rid="bibd2e40"/> and while we may wonder whether any book on Pynchon&#8217;s vast, complex fictional world can truly be more than an &#8216;introduction&#8217;, Malpas and Taylor are indeed stimulating.  Their study provides a clear, lucid discussion of several key themes in Pynchon&#8217;s novels, chief amongst which are paranoia, the emancipatory power of fantasy and alternative modes of perception, and the &#8216;subjunctive potentiality&#8217; (3) of spaces of resistance.  Malpas and Taylor&#8217;s analysis is always illuminating, and their analysis of space in particular ensures that their book is a significant contribution to the diffuse field of Pynchon scholarship.</p>
          <p>   Chapter One focuses on three of the stories published in <italic>Slow Learner</italic>. &#8216;Low-lands&#8217; is placed in its historical and cultural context, with incisive readings of 1950s cultural critiques by figures such as David Riesman and C. Wright Mills, who argued that &#8216;[t]he success of American capitalism had led[&#8230;]to the occlusion of dissenting voices from debates about national identity&#8217; (14).  Characteristically of their book, Malpas and Taylor examine space, warning that the apparent promise in &#8216;Low-lands&#8217; of &#8216;a renewed privatised space and a reconstituted individuality&#8217; (15) may be illusory, as the story&#8217;s ending suggests.  &#8216;The Secret Integration&#8217; is read in conjunction with Pynchon&#8217;s article &#8216;A Journey Into the Mind of Watts&#8217;, with the authors sensitively charting the disparities between white and black experiences of life, as well as the attempt of the story&#8217;s children, through their imagined black companion, to resist the racialising discourse of their parents. Malpas and Taylor state that ultimately &#8216;imaginative intent is obstructed by entropic reality&#8217; (31), an observation that frequently crops up in their later discussions of attenuated resistance.  Entropy itself, and &#8216;Entropy&#8217;, is the next topic explored, with clear and concise summaries of the thought of those &#8211; Norbert Wiener and Henry Adams &#8211; who influenced Pynchon&#8217;s understanding of entropy as a concept.  Effectively contrasting Adams, who &#8216;applied the second law of thermodynamics to all processes and systems&#8217; (35), with Wiener, whose conception of entropy allows for less than total pervasiveness, Malpas and Taylor identify in &#8216;Entropy&#8217; &#8216;a contrapuntal alternation between a view of the world as rational and contained[&#8230;]and one that contains the possibilities of disruption and chance&#8217; (37).  In its appreciation of space and resistance in <italic>Slow Learner</italic>, this chapter effectively introduces the key themes of Malpas and Taylor&#8217;s book as a whole, and anticipates the extension of these concerns to Pynchon&#8217;s novels in its later chapters.</p>
          <p>   Chapter Two concerns not <italic>V.</italic>, Pynchon&#8217;s next work, but <italic>The Crying of Lot 49</italic>. Malpas and Taylor&#8217;s introductory chapter seeks to justify this achronological sequence by stating that &#8216;<italic>Slow Learner </italic>and <italic>The Crying of Lot 49</italic>[&#8230;]are taken as concentrated embodiments of the theoretical and contextual obsessions of a long writing career, but are in no way to be regarded as templates against which Pynchon&#8217;s other work is to be measured&#8217; (6).  The authors go to some trouble to explain their appropriation of <italic>Lot 49 </italic>as &#8216;emblematic of the complexities of Pynchon&#8217;s work&#8217; (48), but the idea that any novel, no matter how brief, can be a &#8216;concentrated embodiment&#8217; of Pynchon&#8217;s writing fails to quite convince, considering the significant variation in style and theme across his oeuvre.  Happily, Malpas and Taylor&#8217;s analysis of <italic>Lot 49</italic> is stimulating regardless of its placement in the book.  The novel is considered as a detective story, after Edward Mendelson&#8217;s influential essay (52), taking the novel&#8217;s lack of closure, despite its proliferation of clues for Oedipa the &#8216;detective&#8217;, as crucial.  The authors see the world of <italic>Lot 49</italic> as a matrix of competing interpretative strategies in which meaning is not an answer but a &#8216;medium&#8217; (54).  For readers, characters and critics alike &#8211; Malpas and Taylor provide a pr&#233;cis of two fundamentally different essays on <italic>Lot 49</italic> in support of this argument<xref ref-type="fn" rid="bibd2e82"/> &#8211; the novel is a maelstrom of intertexts, plots and referentialities that can be interpreted almost <italic>ad infinitum</italic>.  This analysis of the novel usefully anticipates Malpas and Taylor&#8217;s examination of the complex openness of texts such as <italic>Against the Day </italic>and <italic>Gravity&#8217;s Rainbow</italic>.</p>
          <p>   Chapter Three looks at plotting in <italic>V.</italic>, both in the narrative and conspiratorial senses; as in <italic>Lot 49</italic>, &#8216;[t]he world produced by the novel&#8217;s plots[&#8230;]remain[s] just at the limits of what can be grasped&#8217; (76).  Malpas and Taylor explore the contrast between the &#8216;chaotic and never fully engaged wandering of Profane&#8217;, and &#8216;the obsessively ordered &#8220;hot-house&#8221;&#8217; of Stencil&#8217;s &#8216;plotting&#8217; (75), asserting that they are more alike than some might realise; Stencil is barely more engaged with history than Profane, as thanks to his obsession with V. he &#8216;displays an attitude so obsessively focused on a single figure that all other events, even those involving the most extreme suffering and horror, appear only on the sidelines&#8217; (79).  Malpas and Taylor share Stencil&#8217;s concern with V. (though not its intensity), looking at intertexts of V. and <italic>V.</italic> through a survey of previous discussions of the novel&#8217;s relation to modernism, from Maarten van Delden&#8217;s conception of the novel as satirising modernist ideas of coherence and art&#8217;s autonomy (82-4) to John Dugdale&#8217;s presentation of <italic>V.</italic> as an interrogation of the &#8216;violence that lies beneath the &#8220;mystique&#8221; of the modernist image&#8217; (84). Moving from modernism to postmodernism via a Huyssen-inflected examination of Pynchon&#8217;s equal and often concomitant use of &#8216;high&#8217; and &#8216;low&#8217; art (86), Malpas and Taylor demonstrate how <italic>V</italic>.&#8217;s characters are &#8216;aware of their implication in a field of prior texts and contexts&#8217; (88), going on to discuss the novel&#8217;s treatment of gender and bodily transformation, both of which disrupt the idea of the human as postmodernism does (89).  <italic>V.</italic> is shown to be a novel that, through its plots, dislocates both humanity and the possibility of interpretation.</p>
          <p>   Chapter Four looks at <italic>Gravity&#8217;s Rainbow</italic>, and how it, even more so than Pynchon&#8217;s previous works, &#8216;piles complexity upon complexity&#8217; (100), by &#8216;putting at stake the very possibility of reading and by presenting interpretation as a mode of paranoia&#8217; (101). Taking Brian McHale&#8217;s influential analysis of the novel as precluding any concrete meaning as their starting point, as well as the critical approaches from their previous three chapters, Malpas and Taylor explore the novel&#8217;s anti-foundationalism and its multiple modes and genres of representation (103).  Of particular interest is the chapter&#8217;s treatment of space, which becomes a central concern in the remainder of the study.  The Zone is seen as &#8216;an anarchic space of possibility and competition from which the new, post-war world will be born&#8217; (107), but as always Malpas and Taylor stress that hope for the future, and the possibility of a space that will become truly resistant to capitalism and the preterition felt by virtually all the characters in the novel (113), is attenuated.  As the novel is one of pervasive preterition, the authors go on to emphasise, rightly, how the &#8216;elect&#8217; are &#8216;present only as a paranoid projection of an undefinable and inaccessible &#8220;They&#8221;&#8217; (113), parlaying this trenchant observation into a discussion of interpretation-as-paranoia, suggesting that this equivalence is so for both character and reader (115).  This chapter, as with Malpas and Taylor&#8217;s other chapters on Pynchon&#8217;s longer, more complex novels, is profoundly concerned with the difficulty of interpretation and reading, and throughout their book the two handle their appreciation of these difficulties with aplomb, offering rich ways into the text in lieu of the possibility of a coherent &#8216;reading&#8217;.</p>
          <p>   Chapter Five opens by asserting that <italic>Vineland</italic>, with its mimesis of governmental paranoia, has &#8216;accrued a renewed sense of significance&#8217; (126) since 9/11 and the War on Terror.  Sadly there is no extended elaboration upon this interesting observation, which is a shame, particularly considering that Malpas and Taylor&#8217;s discussion of echoes of 9/11 in the chapter on <italic>Against the Day</italic> is done so well.  This is not to say, however, that the chapter&#8217;s exploration of government oppression, and resistance thereto, is not illuminating.  Against Alec McHoul and Ellen Friedman&#8217;s criticisms of <italic>Vineland</italic> as &#8216;nostalgic&#8217;, Malpas and Taylor write that &#8216;Pynchon is able to establish a complex series of contrasts and continuations that work to disabuse the reader of any sense that the book is trading in the easy comforts of nostalgia for an earlier, more authentic moment&#8217; (128).  For them, <italic>Vineland</italic> simultaneously &#8216;expos[es] those spectral traces of an alternative identity that attempt to resist the rationalising logic of modernity&#8217;, and demonstrates &#8216;Pynchon&#8217;s interest in the gradual co-opting of the counterculture by the government and media alike&#8217; (130).  As always in Pynchon, resistance exists more as potentiality than effective practice.  Through a reading of the na&#239;ve, idealistic efforts of 24fps, the deterritorialising and co-opting effect of television and the novel&#8217;s precarious spaces of resistance, Malpas and Taylor show that, unlike in <italic>Gravity&#8217;s Rainbow</italic>, &#8216;[e]lect and preterite are often on close speaking/trading terms&#8217; (146). As such, the tendrils of government, more hands-on than the shadowy &#8216;They&#8217; of the earlier novel, are everywhere, with the same result &#8211; spaces of resistance are only such in terms of <italic>potentiality</italic>.</p>
          <p>   Chapter Six, as one would expect from an examination of <italic>Mason &amp; Dixon</italic>, a novel about a pair of cartographers, is profoundly concerned with space.  According to Malpas and Taylor, &#8216;the line[&#8230;]inaugurates a wider meditation on the centrality of divisions and demarcations in the American national narrative, their persecutory effect and their usefulness in establishing forms of instructive difference&#8217; (154).  The ideological effect of space &#8211; &#8216;the stabilising impetus of mapping&#8217; (163) &#8211; is central to this chapter, as is resistance to the cartography of the elect by America&#8217;s geography and its peoples; in Pynchon&#8217;s depiction of the disenfranchised Native Americans, &#8216;the ethnic rationalisation of continental space that the Mason-Dixon Line inscribes is contested by an indigenous population with an alternative geographical sensibility&#8217; (170).  This chapter, like the previous one, focuses on the &#8216;spectral traces&#8217; of an alternative spatial and ideological sensibility, suggested by, for example, &#8216;a focus on magic and the supernatural, and[&#8230;]the playfulness of language itself&#8217; (164).  The biggest strength of Malpas and Taylor&#8217;s book is the work it does to uncover the spatiality of Pynchon, and in its assessment of <italic>Mason &amp; Dixon</italic> it does so particularly strongly.</p>
          <p>   Chapter Seven covers <italic>Against the Day</italic>, Pynchon&#8217;s longest novel. Stating from the outset that any attempt at countermanding the disorientation and displacement felt by the reader is futile, the chapter posits that the book does not just explore historical anarchism, but is itself an example of &#8216;<italic>aesthetic </italic>anarchy&#8217; (185).  As with <italic>Gravity&#8217;s Rainbow</italic>, the very difficulty of finding meaning in a complex Pynchonian novel is the subject of inquiry, and it is a fruitful way of reading both texts. As a way of providing structure to a reading of this anarchy, Malpas and Taylor relate <italic>Against the Day</italic> to their previous concerns, from spaces of resistance (now more global than ever) to &#8216;American history[&#8230;]as a repeated narrative of aspiration giving way to disappointment&#8217; (186).  The totalising effect of the reductive perspectives of technology and capitalism is of importance, and once more Malpas and Taylor assert that &#8216;Pynchon&#8217;s preterite figures are characteristically resilient, ghostly spectres of a system that has exiled them but which cannot completely erase their traces&#8217; (192).  The end of the chapter states,</p>
          <disp-quote>
            <p>Our belief that the Chums[&#8230;]will remain immune from the forces of political tension can only be a tentative one. But it is a hope that is nevertheless reinforced by a novel that, through its structural extravagance as well as its political thematics, has the capacity to open readers&#8217; eyes to the potential for alternative ways of seeing (207).</p>
          </disp-quote>
          <p>The potentiality of resistance through new ways of &#8216;reading&#8217; both literature and the world is most vividly covered in this chapter, which suggests that Pynchon&#8217;s longest, most complex novels, while challenging, also offer the reward of new meanings and interpretations which, while they may not carry political power, have a power of their own to discursively shape human experience.</p>
          <p>   The book&#8217;s conclusion takes Michiko Kakutani&#8217;s influential designation of <italic>Inherent Vice</italic> as &#8216;Pynchon Lite&#8217; &#8211; a relatively straightforward shorter novel in the &#8216;recognisable generic form of private-eye fiction&#8217; (212) &#8211; as its starting point.  Malpas and Taylor discuss the novel in terms of the concerns of their previous chapters, with the 1960s, California, literary form, resistance and paranoia being paramount.  The chapter is half the length of the previous ones, and <italic>Inherent Vice</italic> is compared with six other Pynchon novels, with the result being that each comparison lacks the depth of the excellent work of the rest of Malpas and Taylor&#8217;s book. Not quite &#8216;Criticism Lite&#8217;, but it is a shame that a novel so often slighted by reviewers as insubstantial should be itself subject to a relatively insubstantial critique.  However, this is not to detract from the coherent and lucid work of the book as whole, nor its importance to the field, particularly to Pynchon scholars interested in space.  Malpas and Taylor deliver on their editor&#8217;s promise of a &#8216;stimulating thesis&#8217;, and then some.</p>
        </sec>
      </body>
      <back>
        <fn-group>
          <fn id="bibd2e40">
            <p> Nahem Yousaf and Sharon Monteith, &#8216;Series Editors&#8217; Foreword&#8217;, Simon Malpas and Andrew Taylor, <italic>Thomas Pynchon</italic> (Manchester University Press, 2013), vi.</p>
          </fn>
          <fn id="bibd2e82">
            <p> Mendelson, Edward (ed.), <italic>Pynchon: A Collection of Critical Essays</italic>, (Englewood Cliffs, NJ: Prentice-Hall, 1978); Colin Nicholson and Randall Stevenson, &#8216;&#8220;Words You Never Wanted to Hear&#8221;: Fiction, History and Narratology in <italic>The Crying of Lot 49</italic>&#8217;, <italic>Pynchon Notes</italic> 16 (1985), 89-109.</p>
          </fn>
        </fn-group>

        <ref-list>
          <ref id="ref-1">
            <element-citation publication-type="journal">
              <person-group person-group-type="author">
                <name>
                  <surname>Nicholson</surname>
                  <given-names>Colin</given-names>
                </name>
                <name>
                  <surname>Stevenson</surname>
                  <given-names>Randall</given-names>
                </name>
              </person-group>
              <article-title>&#8216;Words You Never Wanted to Hear&#8217;: Fiction, History and Narratology in <italic>The Crying of Lot 49</italic></article-title>
              <source>Pynchon Notes</source>
              <date>
                <year>1985</year>
              </date>
              <issue>16</issue>
              <fpage>89</fpage>
              <lpage>109</lpage>
            </element-citation>
          </ref>

          <ref id="ref-2">
            <element-citation publication-type="bookchapter">
              <person-group person-group-type="author">
                <name>
                  <surname>Mendelson</surname>
                  <given-names>Edward</given-names>
                </name>
              </person-group>
              <chapter-title>The Sacred, the Profane and <italic>The Crying of Lot 49</italic></chapter-title>
              <source>Pynchon: A Collection of Critical Essays</source>
              <person-group person-group-type="editor">
                <name>
                  <surname>Mendelson</surname>
                  <given-names>Edward</given-names>
                </name>
              </person-group>
              <date>
                <year>1978</year>
              </date>
              <publisher-loc>Englewood Cliffs, NJ</publisher-loc>
              <publisher-name>Prentice-Hall Inc</publisher-name>
              <fpage>112</fpage>
              <lpage>146</lpage>
            </element-citation>
          </ref>

          <ref id="ref-3">
            <element-citation publication-type="bookchapter">
              <person-group person-group-type="author">
                <name>
                  <surname>Yousaf and Sharon Monteith</surname>
                  <given-names>Nahem</given-names>
                </name>
                <name>
                  <surname>Monteith</surname>
                  <given-names>Sharon</given-names>
                </name>
              </person-group>
              <article-title>Series Editors' Foreword</article-title>
              <source>Thomas Pynchon</source>
              <person-group person-group-type="editor">
                <name>
                  <surname>Malpas</surname>
                  <given-names>Simon</given-names>
                </name>
                <name>
                  <surname>Taylor</surname>
                  <given-names>Andrew</given-names>
                </name>
              </person-group>
              <publisher-name>Manchester University Press</publisher-name>
              <publisher-loc>Manchester</publisher-loc>
              <date>
                <year>2013</year>
              </date>
              <fpage>vi</fpage>
            </element-citation>
          </ref>
        </ref-list>
      </back>
    </article>

And there you have it.