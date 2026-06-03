{
	"translatorID": "1689fc19-2732-47a2-a342-c54d29c7f477",
	"label": "Custom Book",
	"creator": "Martin Paul Eve",
	"target": "",
	"minVersion": "3.0.4",
	"maxVersion": "",
	"priority": 300,
	"inRepository": true,
	"translatorType": 4,
	"browserSupport": "gcsibv",
	"lastUpdated": "2020-04-10 12:47:37"
}

/*
	***** BEGIN LICENSE BLOCK *****

	Copyright © 2020 Martin Paul Eve
					 http://zotero.org

	This file is part of Zotero.

	Zotero is free software: you can redistribute it and/or modify
	it under the terms of the GNU Affero General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	Zotero is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with Zotero.  If not, see <http://www.gnu.org/licenses/>.

	***** END LICENSE BLOCK *****
*/

var namespaces = {};
var _itemType;
var _tags = {};

function setPrefixRemap(map) {
	_prefixRemap = map;
}

function remapPrefix(uri) {
	if(_prefixRemap[uri]) return _prefixRemap[uri];
	return uri;
}

function getPrefixes(doc) {
	var links = doc.getElementsByTagName("link");
	for(var i=0, link; link = links[i]; i++) {
		// Look for the schema's URI in our known schemata
		var rel = link.getAttribute("rel");
		if(rel) {
			var matches = rel.match(/^schema\.([a-zA-Z]+)/);
			if(matches) {
				var uri = remapPrefix(link.getAttribute("href"));
				//Zotero.debug("Prefix '" + matches[1].toLowerCase() +"' => '" + uri + "'");
				_prefixes[matches[1].toLowerCase()] = uri;
			}
		}
	}

	//also look in html and head elements
	var prefixes = (doc.documentElement.getAttribute('prefix') || '')
		+ (doc.head.getAttribute('prefix') || '');
	var prefixRE = /(\w+):\s+(\S+)/g;
	var m;
	while(m = prefixRE.exec(prefixes)) {
		var uri = remapPrefix(m[2]);
		Z.debug("Prefix '" + m[1].toLowerCase() +"' => '" + uri + "'");
		_prefixes[m[1].toLowerCase()] = uri;
	}
}

function detectWeb(doc, url) {
	//blacklist wordpress jetpack comment plugin so it doesn't override other metadata
	if(exports.itemType) return exports.itemType;

	init(doc, url, Zotero.done);
}

function loadTags(doc, hwType) {
	var metaTags = doc.head.getElementsByTagName("meta");
	Z.debug("Book Metadata: found " + metaTags.length + " book tags.");

	for(var i=0, metaTag; metaTag = metaTags[i]; i++) {
		var tags = metaTag.getAttribute("name");
		if (!tags) tags = metaTag.getAttribute("property");
		var value = metaTag.getAttribute("content");
		if(!tags || !value) continue;
		if(tags.startsWith('book')) {
			Z.debug(tags + " -> " + value);
			_tags[tags] = value;
	
			tags = tags.split(/\s+/);
			hwType = "book"; // Unlikely, but other item types may have ISBNs as well (e.g. Reports?)
		}
	}
}

function init(doc, url, callback, forceLoadRDF) {
	getPrefixes(doc);
	
	var hwType, hwTypeGuess, generatorType, statements = [];

	loadTags(doc, hwType);
	
	if(Object.keys(_tags).length > 0) {
		hwType = 'book';
	}
	
	Z.debug(_tags.length);
	Z.debug(hwType);

	callback(exports.itemType || hwType || hwTypeGuess || generatorType);
	
}

// used to retrieve next COinS object when asynchronously parsing COinS objects
// on a page
function retrieveISBN(item) {

	Z.debug("Retrieveing ISBN");
	var search = Zotero.loadTranslator("search");
	search.setHandler("itemDone", function(obj, newItem) {
		supplementItem(newItem, item, [], ['contextObject', 'repository']);
		newItem.complete();
	});
	search.setHandler("done", function() {
		Z.debug("Done");
	});
	// Don't throw on error
	search.setHandler("error", function() {
		Zotero.debug("Failed to look up item:");
		Zotero.debug(item);
	});
	// look for translators
	search.setHandler("translators", function(obj, translators) {
		if(translators.length) {
			search.setTranslator(translators);
			search.translate();
		} else {
			Z.debug("Done");
		}
	});
	
	search.setSearch(item);
	search.getTranslators();
}

function supplementItem(item, supp, prefer, ignore) {
	if (!prefer) prefer = [];
	if (!ignore) ignore = [];
	
	for(var i in supp) {
		if (ignore.indexOf(i) != -1)  continue;
		if (i == 'creators' || i == 'attachments' || i == 'notes'
			|| i == 'tags' || i == 'seeAlso'
		) {
			if ( (item.hasOwnProperty(i) && item[i].length) // Supplement only if completely empty
				|| (!supp[i].length || typeof supp[i] == 'string')
			) {
				continue;
			}
		} else if (!supp.hasOwnProperty(i)
			|| (item.hasOwnProperty(i) && prefer.indexOf(i) == -1)) {
			continue;
		}

		Z.debug('Supplementing item.' + i);
		item[i] = supp[i];
	}

	return item;
}

function doWeb(doc, url) {
	//set default namespace
	namespaces.x = doc.documentElement.namespaceURI;
	
	newItem = new Zotero.Item("book");
	
	newItem.title = ' ';
	
	hwType = [];
	
	loadTags(doc, hwType);
	
	var ISBN = _tags['book_isbn'];
	Z.debug("ISBN INFO");
	
	newItem.ISBN = ISBN;
	
	addPDF(doc, newItem);
	
	retrieveISBN(newItem);
}


/**
 * Adds the PDF
 */
function addPDF(doc, newItem) {
	//This may not always yield desired results
	//i.e. if there is more than one pdf attachment (not common)
	pdfURL = _tags['book_pdf_url'];
	
	//delete any pdf attachments if present
	//would it be ok to just delete all attachments??
	for(var i=newItem.attachments.length-1; i>=0; i--) {
		if(newItem.attachments[i].mimeType == 'application/pdf') {
			newItem.attachments.splice(i, 1);
		}
	}

	newItem.attachments.push({title:"Full Text PDF", url:pdfURL, mimeType:"application/pdf"});
}

var exports = {
	"doWeb": doWeb,
	"detectWeb": detectWeb,
	"itemType": false,
	//activate/deactivate splitting tags in final data cleanup when they contain commas or semicolons
	"splitTags": true,
	"fixSchemaURI": setPrefixRemap
}

