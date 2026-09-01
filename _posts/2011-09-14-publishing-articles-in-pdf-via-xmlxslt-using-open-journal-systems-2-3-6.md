---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/09/14/publishing-articles-in-pdf-via-xmlxslt-using-open-journal-systems-2-3-6
categories:
- Publishing Technology
- Programming
comments: []
date: 2011-09-14 11:28:17 +0200
date_gmt: 2011-09-14 11:28:17 +0200
doi: https://doi.org/10.59348/7hd2c-n7m52
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- OJS
- Publishing
- plugin
title: Publishing articles in PDF via XML/XSLT using Open Journal Systems 2.3.6
wordpress_id: 1472
wordpress_url: https://www.martineve.com/?p=1472
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mjwpcqs2a"
---

<p>This is a post detailing my experiments with Open Journal Systems 2.3.6 and the current state of producing galleys for an article from a single XML file. As shall be seen in the conclusion, no currently functional plugin allows this feature. This will, therefore, be the first of several posts that will cover not only writing an OJS plugin from scratch, but also aim to fill this gap.</p>
<p><img src="https://www.martineve.com/wp-content/uploads/2011/09/PDF_Large-e1315999660401.jpg" alt="PDF" title="PDF_Large" style="width:750px;" class="alignnone size-full wp-image-1481" /></p>
<p>At present OJS contains a plugin called XMLGalley which is designed, in principle, to allow generation of article galleys, on the fly, from an XML file. There is support in this module for PDF generation and, in previous iterations, this was "working". I put scare quotes there because it introduced <a href="http://pkp.sfu.ca/bugzilla/show_bug.cgi?id=5152">a different problem</a> which can be clearly seen in the source of ArticleXMLGalleyDAO.inc.php:</p>

{% highlight php %}
// WARNING: The below code is disabled because of bug #5152. When a galley
// exists with the same galley_id as an entry in the article_xml_galleys table,
// editing the XML galley will corrupt the entry in the galleys table for the
// same galley_id. This has been fixed by retiring the article_xml_galleys
// table's xml_galley_id in favour of using the galley_id instead, but this
// means that only a single derived galley (=XHTML) is possible for an XML
// galley upload.
{% endhighlight %}

<p>As is made clear from the penultimate line, the fix that has been introduced here has been to remove PDF support so that articles are generated purely from XHTML.</p>
<p>Now, how is this working?</p>
<p>The key to working out the flow in an OJS plugin is to identify the hooks it deploys. In this case XMLGalleyPlugin.inc.php provides the necessary info:</p>

{% highlight php %}
// NB: These hooks essentially modify/overload the existing ArticleGalleyDAO methods
HookRegistry::register('ArticleGalleyDAO::getArticleGalleys', array(&$xmlGalleyDao, 'appendXMLGalleys') );
HookRegistry::register('ArticleGalleyDAO::insertNewGalley', array(&$xmlGalleyDao, 'insertXMLGalleys') );
HookRegistry::register('ArticleGalleyDAO::deleteGalleyById', array(&$xmlGalleyDao, 'deleteXMLGalleys') );
HookRegistry::register('ArticleGalleyDAO::incrementGalleyViews', array(&$xmlGalleyDao, 'incrementXMLViews') );
HookRegistry::register('ArticleGalleyDAO::_returnGalleyFromRow', array(&$this, 'returnXMLGalley') );
HookRegistry::register('ArticleGalleyDAO::getNewGalley', array(&$this, 'getXMLGalley') );

// This hook is required in the absence of hooks in the viewFile and download methods
HookRegistry::register( 'ArticleHandler::viewFile', array(&$this, 'viewXMLGalleyFile') );
HookRegistry::register( 'ArticleHandler::downloadFile', array(&$this, 'viewXMLGalleyFile') );
{% endhighlight %}

<p>The most important hooks for our purposes of understanding are insertXMLGalleys (fired when the user uploads an XML galley) and viewXMLGalleyFile (called when the user attempts to download a PDF).</p>
<p>Now, at present, the insertXMLGalleys function has the following code commented out, in support of bug #5152:</p>

{% highlight php %}
/*

			// if we have enabled XML-PDF galley generation (plugin setting)
			// and are using the built-in NLM stylesheet, append a PDF galley as well
			$journal =& Request::getJournal();
			$xmlGalleyPlugin =& PluginRegistry::getPlugin('generic', $this->parentPluginName);

			if ($xmlGalleyPlugin->getSetting($journal->getId(), 'nlmPDF') == 1 && 
				$xmlGalleyPlugin->getSetting($journal->getId(), 'XSLstylesheet') == 'NLM' ) {

				// create a PDF galley
				$this->update(
					'INSERT INTO article_xml_galleys
						(galley_id, article_id, label, galley_type)
						VALUES
						(?, ?, ?, ?)',
					array(
						$galleyId,
						$galley->getArticleId(),
						'PDF',
						'application/pdf'
					)
				);

			}*/
{% endhighlight %}

<p>Reading this, it is clear that the way the code originally was working was to insert an entry into the article_xml_galleys with the "application/pdf" mime type in addition to the xhtml rendered markup.</p>
<p>As this no longer works, the aim of this project, the source of which is <a href="https://github.com/MartinPaulEve/MEXMLGalley">at my GitHub</a> (with virtually no content there at present), will be to write a plugin which would also hook into insertXMLGalleys, run the PDF transform on the XML file, store the file in the article_files table and add a PDF galley, at this stage, to the native article_files table.</p>
<p>Stay tuned for the next installment...</p>
<p><i>Featured image by <a href="http://www.flickr.com/photos/rillian">rillian</a> under a CC-BY-SA license.</i></p>