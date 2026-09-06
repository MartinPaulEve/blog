---
archive: https://wayback.archive-it.org/22123/20241101171236/https://eve.gd/2025/10/09/using-a-public-api-or-the-instability-of-musicbrainz-ids
date: 2025-10-09
last_modified_at: 2026-09-06
doi: https://doi.org/10.59348/q9qkk-eyx15
roguescholar: https://rogue-scholar.org/records/r5pxf-5mv41
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lvqjwzg2f
image:
  feature: header_geek.png
layout: post
ogImage: images/header_geek.png
title: Using a public API, or the instability of MusicBrainz IDs
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lvqjwzg2f"
categories:
- Programming
- Music
kcworks: https://works.hcommons.org/records/bv5vk-78k85
references:
- title: tici taci
  type: WebSite
  url: https://ticitaci.com
- title: Martin Eve
  type: WebPage
  url: https://ticitaci.com/artists/martin-eve.html
  isPartOf:
    name: tici taci
    type: WebSite
- https://musicbrainz.org/label/62db3e96-423a-4e9d-bf66-7a017f1dfc73 # Ticitaci MusicBrainz label record
- https://musicbrainz.org/release/a82fd9b7-4129-4e44-8867-a1a21493ee8e # MusicBrainz release (redirected, old ID)
- https://musicbrainz.org/release/114bdc29-02ca-45e8-83cb-9b2dae354e20 # MusicBrainz release (new canonical ID)
---

I have a script (a custom static site generator) that produces the output at [https://ticitaci.com](https://ticitaci.com) -- a page for the record label [on which I have released music](https://ticitaci.com/artists/martin-eve.html) (and that I really, really love).

It generates the data [from the MusicBrainz records](https://musicbrainz.org/label/62db3e96-423a-4e9d-bf66-7a017f1dfc73), which I maintain. I have a load of local files that the script uses to generate the pages. For example the soundcloud records are all stored in files such as input/soundcloud/a82fd9b7-4129-4e44-8867-a1a21493ee8e.soundcloud. If you look up [https://musicbrainz.org/release/a82fd9b7-4129-4e44-8867-a1a21493ee8e](https://musicbrainz.org/release/a82fd9b7-4129-4e44-8867-a1a21493ee8e), you will see that you come to the release page for my track, “Losing It”.

However, I recently noticed that the IDs that I was getting back were not corresponding to the files I had on disk. For example: [https://musicbrainz.org/release/a82fd9b7-4129-4e44-8867-a1a21493ee8e](https://musicbrainz.org/release/a82fd9b7-4129-4e44-8867-a1a21493ee8e) actually redirects you to [https://musicbrainz.org/release/114bdc29-02ca-45e8-83cb-9b2dae354e20](https://musicbrainz.org/release/114bdc29-02ca-45e8-83cb-9b2dae354e20). Someone has done a merge at some point and a NEW identifier has been generated for the release. The old one DOES redirect, but the data I was getting back no longer corresponds to the ID that I had on disk and so I can't match up the local files in my generator. Here's what I get back:

	{
	  "release": {
	    "id": "114bdc29-02ca-45e8-83cb-9b2dae354e20",
	    "title": "Losing It",
	    "status": "Official",
	    "quality": "normal",
	    "packaging": "None",
	    "text-representation": {
	      "language": "eng",
	      "script": "Latn"
	    },
	    "date": "2021-12-17",
	    "country": "GB",
	    "release-event-list": [
	      {
	        "date": "2021-12-17",
	        "area": {
	          "id": "8a754a16-0027-3a29-b6d7-2b40ea0481ed",
	          "name": "United Kingdom",
	          "sort-name": "United Kingdom",
	          "iso-3166-1-code-list": [
	            "GB"
	          ]
	        }
	      }
	    ],
	    "release-event-count": 1,
	    "barcode": "5060913709754",
	    "cover-art-archive": {
	      "artwork": "true",
	      "count": "1",
	      "front": "true",
	      "back": "false"
	    }
      }
	}


The solution is relatively easy: I have written a scanner that looks for changed IDs (where the result that comes back is different to the input) and then renames the files on local disk. However, it's really bad form for identifiers to move around in this way. I had assumed that these IDs wouldn't change (and, apparently, they don't, it's just that if entities are merged (e.g., duplicate artists combined), one MBID is kept as the primary identifier and the others redirect to it), but that I could rely on the ID I put in being returned by the API, even if it's a redirect. Perhaps there is some way inside MusicBrainz to see *LINKED* IDs? I can't find it in the documentation -- I just get a redirect, which then confuses my local file correlations (and if you used a database, you'd have the same problems). There is a field called “alias”. Is this it? Who knows? I think it's more likely that this is an alias for different artist names (not-so-secret tici taci fact: Mr Cogs is Duncan Gray, the label boss). There is also the option to include more fields, which I use, but I can't find out easily whether any of these has a merge history.

Basically, this was a disappointing case of an identifier changing under my feet, as I was using it locally. A redirect on an API is not enough if you rely on matching up the expected ID to data in templates and so on. APIs should provide a history of why an identifier is redirecting, if it changes, with information about the redirects to it. This doesn't do that, as far as I can see.