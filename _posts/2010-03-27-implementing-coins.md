---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2010/03/27/implementing-coins
categories:
- Scholarly Communications
comments: []
date: 2010-03-27 12:08:00 +0100
date_gmt: 2010-03-27 12:08:00 +0100
doi: https://doi.org/10.59348/4mr2f-ybq70
roguescholar: https://rogue-scholar.org/records/xmbca-2bq53
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmbo4hm2s
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- COinS
title: Implementing COinS
wordpress_id: 22
wordpress_url: http://new.martineve.com/?p=22
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mmbo4hm2s"
kcworks: https://works.hcommons.org/records/7er1y-qrj37
---

<p><img src="/images/uploads/2010/03/Bookshelf_photo-300x228.jpg" alt="Rows of books lined up on a bookshelf" width="500" height="380"/></p>
<p>After the Vitae Digital Researcher workshop at the British Library, I decided to ramp up my web presence to a slightly more professional level than it had previously obtained.
 Having also decided that it would be nice to take a bit of a break this weekend, I went ahead and implemented COinS on my main web page. Although, at present, my publication list is somewhat insubstantial, as this grows it will be possible for anyone who visits to automatically import my conference papers and publications into social citation software such as Zotero, Mendeley and CiteULike.
 COinS works by embedding a span tag inside your document that describes the data being visually presented. The full specification is at <a href="http://ocoins.info/">http://ocoins.info/</a>
 However, I anticipate that this will merely end up scaring quite a few people off, so here's a quick example that makes it much easier to digest. There's also an automatic generator at <a href="http://generator.ocoins.info/">http://generator.ocoins.info</a>, although this won't do conference papers, which is what I will show below.</p>
 <p>The example!</p>
 <p>On my site, I have the following code embedded:</p>

{% highlight html %}
 <cite>&lt;span class="Z3988" title="ctx_ver=Z39.88-2004&amp;amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Abook&amp;amp;rfr_id=info%3Asid%2Focoins.info%3Agenerator&amp;amp;rft.btitle=%27It+sure%27s+hell+looked+like+war%27%3A+Terrorism+and+the+Cold+War+in+Thomas+Pynchon%27s+Against+the+Day+and+Don+DeLillo%27s+Underworld%27&amp;amp;rft.creator=Martin+Paul+Eve&amp;amp;rft.publisher=Maria+Curie-Sklodowska+University&amp;amp;rft.date=2010-06-09&amp;amp;rft.format=Conference+Paper&amp;amp;rft.source=IPW+2010%3A+Of+Pynchon+And+Vice%3A+America%27s+Inherent+Others&amp;amp;rft.genre=conference"&gt;'It sure's hell looked like war': Terrorism and the Cold War in Thomas Pynchon's &lt;i&gt;Against the Day&lt;/i&gt; and Don DeLillo's &lt;i&gt;Underworld&lt;/i&gt;' (forthcoming, &lt;i&gt;IPW 2010: Of Pynchon And Vice: America's Inherent Others&lt;/i&gt;, Maria Curie-Sklodowska University, Lublin, Poland)&lt;/span&gt;</cite>
 
 {% endhighlight %}


 <p>What does this do?</p>
 <p>Well, to start at the end, the last portion "'It sure's hell looked like war': Terrorism and the Cold War in Thomas Pynchon's &lt;i&gt;Against the Day&lt;/i&gt; and Don DeLillo's &lt;i&gt;Underworld&lt;/i&gt;' (forthcoming, &lt;i&gt;IPW 2010: Of Pynchon And Vice: America's Inherent Others&lt;/i&gt;, Maria Curie-Sklodowska University, Lublin, Poland)" simply displays the name of the paper.</p>
 <p>The portion before is also, not really, so hard to explain.</p>
 <p>To get a human readable version, replace in the above the following:</p>
 &lt;space&gt; --&gt; %20<br /> + --&gt; &lt;space&gt;<br /> # --&gt; %23<br /> % --&gt; %25<br /> &amp; --&gt; %26<br /> '&nbsp;&nbsp; --&gt; %27<br /> + --&gt; %2B&nbsp; <br /> / --&gt; %2F<br /> &lt; --&gt; %3C<br /> = --&gt; %3D<br /> &gt; --&gt; %3E<br /> ? --&gt; %3F<br /> : --&gt; %3A<br /> &eacute; --&gt; %C3%A9<br /> &uuml; --&gt; %C3%BC
 
 <p>So, the title attribute actually reads (with [ENTER] inserted after each &amp;):</p>

{% highlight html %}
 <cite>ctx_ver=Z39.88-2004&amp;<br /> rft_val_fmt=info=ofi/fmt=kev=mtx=book&amp;<br /> rfr_id=info=sid/ocoins.info=generator&amp;<br /> rft.btitle='It sure's hell looked like war'= Terrorism and the Cold War in Thomas Pynchon's Against the Day and Don DeLillo's Underworld'&amp;<br /> rft.creator=Martin Paul Eve&amp;<br /> rft.publisher=Maria Curie-Sklodowska University&amp;<br /> rft.date=2010-06-09&amp;<br /> rft.format=Conference Paper&amp;<br /> rft.source=IPW 2010= Of Pynchon And Vice= America's Inherent Others&amp;<br /> rft.genre=conference</cite>
{% endhighlight %}

 <p>Now, it becomes a bit clearer what's going on. There are a set of key/value pairs specifying each bibliographic aspect.</p>
 <p>Let me run through each key.</p>

{% highlight html %}
 <cite>ctx_ver=Z39.88-2004&amp;</cite>
{% endhighlight %}

<p>This simply tells the parser (Zotero etc.) the version of the metadata format that we are using.</p>

{% highlight html %}
 <cite>rft_val_fmt=info=ofi/fmt=kev=mtx=book&amp;</cite>
{% endhighlight %}

<p>This specifies that the type of publication is a "book". For conference papers, use this and then set the genre (see below).</p>

{% highlight html %}
 <cite>rfr_id=info=sid/ocoins.info=generator&amp;</cite>
{% endhighlight %}

<p>Another piece of data purely for the automated parsers; it should be there, but you don't need to worry about it.</p>

{% highlight html %}
 <cite>rft.btitle='It sure's hell looked like war'= Terrorism and the Cold War in Thomas Pynchon's Against the Day and Don DeLillo's Underworld'&amp;</cite>
{% endhighlight %}

<p>The title of your stunning research. btitle stands for <strong>b</strong>ook <strong>title</strong>.</p>

{% highlight html %}
<cite>rft.creator=Martin Paul Eve&amp;</cite>
{% endhighlight %}

<p>The name of the author.</p>

{% highlight html %}
<cite>rft.publisher=Maria Curie-Sklodowska University&amp;</cite>
{% endhighlight %}

<p>The name of the publisher.</p>

{% highlight html %}
<cite>rft.date=2010-06-09&amp;<br /> </cite><br /> The<strong> </strong>date of publication or, in this example of a conference paper, the date given.
<cite>rft.format=Conference Paper&amp;</cite>
{% endhighlight %}

<p>The format of the piece.</p>

{% highlight html %}
<cite><br /> rft.source=IPW 2010= Of Pynchon And Vice= America's Inherent Others&amp;</cite>
{% endhighlight %}

<p>The&nbsp; conference at which the paper was given.</p>

{% highlight html %}
<cite>rft.genre=conference</cite>
{% endhighlight %}

<p>Finally, specify genre to conference to say that, in reality, it's not a book.</p>
<p>There, demystified. Now, when you visit the page, Zotero or CiteULike should be able to parse the information making you 10x more citable!</p>
<p>I have only tested this example in Zotero and, at present, it is not possible using COinS to get the information about place and conference name into the software (see: <a href="http://forums.zotero.org/discussion/439/coins-conference-papers-imported-incorrectly-by-zotero/">http://forums.zotero.org/discussion/439/coins-conference-papers-imported-incorrectly-by-zotero/</a>). I have included it in the example purely for future proofing.</p>
<p>Photograph for this post is licensed as Attribution-Non-Commercial-Share Alike 2.0 Generic by "Here's Kate" at <a href="http://hereskate.com/blog">http://hereskate.com/blog</a> You must credit the original author, not me, if you re-use it.</p>