---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2020/03/14/i4oc-open-citations-implementation-in-janeway
date: 2020-03-14
doi: https://doi.org/10.59348/vqehm-v5y58
roguescholar: https://rogue-scholar.org/records/h1cj4-rh727
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m6h6dam2f
image:
  feature: oa.png
layout: post
ogImage: images/oa.png
title: I4OC open citations implementation in Janeway
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7m6h6dam2f"
categories:
- Publishing Technology
- Scholarly Communications
kcworks: https://works.hcommons.org/records/q459y-q7n10
---

One of the strongly recommended criteria under Plan S is that journals provide "Openly accessible data on citations according to the standards by the Initiative for Open Citations (I4OC)". This means, essentially, depositing citation data with Crossref and then marking it as open.

This is a tricky task that will be outside of the ability of many smaller publishers. It requires citations to be marked up in a format that distinguishes them from other text. However, for anyone who is producing JATS XML, I have now implemented the ability to deposit citation data in our open-source platform, [Janeway](https://github.com/BirkbeckCTP/janeway).

#How does it work?

1. We generate a standard Crossref DOI template that will work for articles that have, or do not have, XML. Essentially, deposits without JATS XML are unaffected.
2. If there is a JATS XML galley attached as the render galley for an article, we perform an XSL transform that generates the necessary Crossref XML.
3. We deposit the XML with or without citation data.
4. We now also poll Crossref for in progress data on deposit success every 30 minutes if you have a Janeway cron task setup, so you can check on the status of DOIs.

#What JATS is supported?

Any element-citation or mixed-citation is supported.

For example:

<pre>
	&lt;ref id="B1"&gt;
		&lt;label&gt;1&lt;/label&gt;
		&lt;mixed-citation publication-type="journal"&gt;
			&lt;string-name&gt;&lt;surname&gt;Bishop&lt;/surname&gt;, &lt;given-names&gt;S.&lt;/given-names&gt;&lt;/string-name&gt;, 
			&lt;year&gt;2018&lt;/year&gt;. 
			&lt;article-title&gt;&#8216;Anxiety, panic and self-optimization: Inequalities and the YouTube algorithm.&#8217;&lt;/article-title&gt; 
			&lt;source&gt;Convergence&lt;/source&gt;, 
			&lt;volume&gt;24&lt;/volume&gt;(&lt;issue&gt;1&lt;/issue&gt;): &lt;fpage&gt;69&lt;/fpage&gt;&#8211;&lt;lpage&gt;84&lt;/lpage&gt;. DOI: 
			&lt;pub-id pub-id-type="doi"&gt;10.1177/1354856517736978&lt;/pub-id&gt;
		&lt;/mixed-citation&gt;
	&lt;/ref&gt;
</pre>

is translated into:
<pre>
	&lt;citation key="keyref_B1"&gt;
		&lt;journal_title&gt;Convergence&lt;/journal_title&gt;
		&lt;doi&gt;10.1177/1354856517736978&lt;/doi&gt;
		&lt;volume&gt;24&lt;/volume&gt;
		&lt;issue&gt;1&lt;/issue&gt;
		&lt;author&gt;Bishop, S.&lt;/author&gt;
		&lt;first_page&gt;69&lt;/first_page&gt;
		&lt;cYear&gt;2018&lt;/cYear&gt;
		&lt;article_title&gt;
		‘Anxiety, panic and self-optimization: Inequalities and the YouTube algorithm.’
		&lt;/article_title&gt;
	&lt;/citation&gt;
</pre>

This is then appended to the deposit. Items of an unrecognized type are simply passed through as unstructured citations. So, for instance, a web page might appear as:

<pre>
	&lt;citation key="keyref_B5"&gt;
		&lt;unstructured_citation&gt;
			Chan, J., R. Farkas, A. Hirsch, and C. Kinsey, 2012. ‘Becoming Camwhore, Becoming Pizza.’ Mute, 8 November 2012. Available at: http://www.metamute.org/editorial/articles/becoming-camwhore-becoming-pizza [last accessed 26 July 2019].
		&lt;/unstructured_citation&gt;
	&lt;/citation&gt;
</pre>

Submit 'em all and let Crossref sort them out.

In this way, we hope to support those producing JATS in achieving the Plan S technical requirements. We have verified the deposit system against JATS in the