---
title: "FAIR and Square: making a static site support FAIR signposting"
layout: post
doi: "https://doi.org/10.59348/2zdfp-egq38"
image:
  feature: gavel.jpg
  credit: Tingey Injury Lawfirm on Unsplash
  creditlink: "https://unsplash.com/@tingeyinjurylawfirm?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText"
  title: "An image of a judge's hammer and gavel"
archive: "https://wayback.archive-it.org/22123/20241101171236/https://eve.gd/2026/06/27/fair-and-square-making-a-static-site-support-fair-signposting"
references:
  - type: TechArticle
    url: "https://signposting.org/FAIR/"
    title: "FAIR Signposting"
    date: 2023-10-02
    author: ["Herbert Van de Sompel", "Martin Klein", "Shawn Jones", "Michael L. Nelson", "Simeon Warner", "Anusuriya Devaraju", "Robert Huber", "Wilko Steinhoff", "Vyacheslav Tykhonov", "Luc Boruta", "Enno Meijers", "Stian Soiland-Reyes", "Mark Wilkinson"]
  - type: WebSite
    url: "https://chromewebstore.google.com/detail/signposting-sniffing/pahanegeimljfcnjogglnamnlcgipmbc"
    title: "Signposting Sniffing"
    author: "fdo.extensions"
    date: 2025-03-1
  - type: WebSite
    url: "https://pleiades.stoa.org/"
    title: "Pleiades"
    author: "Tom Elliott"
  - https://eve.gd/2026/06/23/making-blog-posts-harvestable-by-zotero-and-preserving-case-in-citation-fields/
  - https://eve.gd/2026/04/19/the-necessary-pain-involved-in-blogging-if-you-want-your-work-to-be-preserved-beyond-your-lifespan/
  - https://doi.org/10.31274/jlsc.16288 # Digital Scholarly Journals Are Poorly Preserved: A Study of 7 Million Articles  
---
After my [previous post about Zotero ingest](/2026/06/23/making-blog-posts-harvestable-by-zotero-and-preserving-case-in-citation-fields/), I wondered what else I might be able to do to make this scholarly (and personal) blog more accessible, navigable, harvestable, and ingestable. One thing that occurred to me, that I had not implemented, is that I might make this blog `FAIR`. That is: [Findable, Accessible, Interoperable, and Reusable](https://www.go-fair.org/fair-principles/).

One of the ways one can work towards this is by implementing the [FAIR Signposting Profile](https://signposting.org/FAIR/). This is a series of in-document metadata elements, but also a linkset in the HTTP header returned by the blog. I am hosting with [Reclaim Hosting](https://www.reclaimhosting.com/), who are using an Apache webserver to serve my static files. Normally I would curse this. Who's running Apache in this day and age? We have many more sophisticated technologies for serving websites. Even nginx would have been better, I would exclaim.

However, this is actually very useful in this circumstance. The Apache web server allows us to put `.htaccess` files in every directory. And directories are how my posts are structured. There is a directory with an index.html file inside it, so you don't have to see that it's a directory, it just looks like a path on the website. When you load `https://eve.gd/2026/06/23/making-blog-posts-harvestable-by-zotero-and-preserving-case-in-citation-fields/` the webserver looks in the blog folder on my server at `/2026/06/23/making-blog-posts-harvestable-by-zotero-and-preserving-case-in-citation-fields/` and serves you the `index.html` file. So you are getting `/2026/06/23/making-blog-posts-harvestable-by-zotero-and-preserving-case-in-citation-fields/index.html`. But it doesn't look like that to the user. However, really, all of these posts are in their own directories. And Apache can take directives from any one of them.

I made a plugin for my static site generator that creates a `.htaccess` file for every post that look like this:

```
<Files "index.html">
Header set Link "<https://orcid.org/0000-0002-5589-8511>; rel=\"author\", <https://doi.org/10.59348/vrt01-f3b49>; rel=\"cite-as\", <https://schema.org/BlogPosting>; rel=\"type\", <https://schema.org/AboutPage>; rel=\"type\", <https://creativecommons.org/licenses/by/4.0/>; rel=\"license\", <https://eve.gd/2026/06/23/making-blog-posts-harvestable-by-zotero-and-preserving-case-in-citation-fields/metadata.json>; rel=\"describedby\"; type=\"application/ld+json\"; profile=\"https://schema.org/\""
</Files>
<Files "metadata.json">
ForceType application/ld+json
</Files>
```

When the user's browser -- or a machine agent -- requests the page, it now gets the following HTTP headers:

> HTTP/2 200 
> 
> last-modified: Fri, 26 Jun 2026 22:19:49 GMT
> 
> accept-ranges: bytes
> 
> content-length: 25244
> 
> content-security-policy: upgrade-insecure-requests
> 
> strict-transport-security: max-age=31536000; includeSubDomains
> 
> x-xss-protection: 1; mode=block
> 
> x-frame-options: SAMEORIGIN
> 
> x-content-type-options: nosniff
> 
> referrer-policy: strict-origin-when-cross-origin
> 
> link: <https://orcid.org/0000-0002-5589-8511>; rel="author", <https://doi.org/10.59348/vrt01-f3b49>; rel="cite-as", <https://schema.org/BlogPosting>; rel="type", <https://schema.org/AboutPage>; rel="type", <https://creativecommons.org/licenses/by/4.0/>; rel="license", <https://eve.gd/2026/06/23/making-blog-posts-harvestable-by-zotero-and-preserving-case-in-citation-fields/metadata.json>; rel="describedby"; type="application/ld+json"; profile="https://schema.org/"
> 
> content-type: text/html; charset=UTF-8
> 
> date: Sat, 27 Jun 2026 09:00:06 GMT

You can see that this allows us to get information about the page without even loading its full HTML content. Useful for machine access and discovery.

My Jekyll plugin also adds a `metadata.json` to every post directory. Here's an example of how that looks:

```json
{
  "@context": "https://schema.org/",
  "@type": "BlogPosting",
  "name": "Making blog posts harvestable by Zotero and preserving case in citation fields",
  "headline": "Making blog posts harvestable by Zotero and preserving case in citation fields",
  "url": "https://eve.gd/2026/06/23/making-blog-posts-harvestable-by-zotero-and-preserving-case-in-citation-fields/",
  "inLanguage": "en-GB",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "author": {
    "@type": "Person",
    "name": "Martin Paul Eve",
    "url": "https://eve.gd",
    "identifier": "https://orcid.org/0000-0002-5589-8511"
  },
  "datePublished": "2026-06-23",
  "identifier": "https://doi.org/10.59348/vrt01-f3b49",
  "citation": [
    {
      "@type": "BlogPosting",
      "@id": "https://paregorios.org/posts/2018/05/zotero_nikola_harmony/",
      "name": "Zotero-Nikola Harmony (One Simple Trick)",
      "url": "https://paregorios.org/posts/2018/05/zotero_nikola_harmony/",
      "datePublished": "2018-05-08",
      "inLanguage": "en",
      "license": "https://creativecommons.org/licenses/by/4.0/",
      "author": {
        "@type": "Person",
        "name": "Tom Elliott",
        "@id": "https://orcid.org/0000-0002-4114-6677",
        "identifier": "https://orcid.org/0000-0002-4114-6677"
      },
      "isPartOf": {
        "@type": "Blog",
        "name": "paregorios.org",
        "url": "https://paregorios.org/"
      }
    }
  ]
}
```

There's descriptive metadata here, including license information, but also, cooly, we have citation information for pages that I cite. I have to enter these citation details manually, but it's good to be contributing to that ole citation network! To generate this, I add:

```yaml
references:
	- type: BlogPosting
	title: "Zotero-Nikola Harmony (One Simple Trick)"
	url: "https://paregorios.org/posts/2018/05/zotero_nikola_harmony/"
	author:
  	name: Tom Elliott
  	orcid: "https://orcid.org/0000-0002-4114-6677"
	date: 2018-05-08
	language: en
	license: "https://creativecommons.org/licenses/by/4.0/"
	isPartOf:
  	type: Blog
  	name: paregorios.org
  	url: "https://paregorios.org/"
```

If you want, then, to verify that it's working, there's quite a good tool called [Signposting Sniffing](https://chromewebstore.google.com/detail/signposting-sniffing/pahanegeimljfcnjogglnamnlcgipmbc), that plugs-into the Chrome browser and will show you whether your FAIR Signposts are working correctly. Here's my result so far and what it looks like:

<img src="/images/fair.jpg" width="100%" alt="A wide golden-yellow notification panel with six lines of dark brown text and orange-red hyperlinks, each followed by a small copy-to-clipboard icon. A small blue circular arrow icon appears at the left of the third line. The text reads: &quot;Signposting.org metadata: this page is authored by https://orcid.org/0000-0002-5589-8511. Signposting.org metadata: this page should be cited as https://doi.org/10.59348/vrl01-53h49. Signposting.org metadata: this page is of the type described at https://schema.org/BlogPosting. Signposting.org metadata: this page is of the type described at https://schema.org/AboutPage. Signposting.org metadata: this page is licensed according to https://creativecommons.org/licenses/by/4.0/. Signposting.org metadata: this page is described by https://eve.gd/2026/06/23/making-blog-posts-harvestable-by-zotero-and-preserving-case-in-citation-fields/metadata.json (application/ld+json) with a profile at https://schema.org/.&quot;">

I also have a cool shortcut for self-citation. If I put this as a single line in the references section:

```yaml
- https://eve.gd/2026/06/23/making-blog-posts-harvestable-by-zotero-and-preserving-case-in-citation-fields/
```

That automatically generates the citation block:

```json
{
  "@type": "BlogPosting",
  "@id": "https://doi.org/10.59348/6cr4z-4ct43",
  "name": "The Necessary Pain Involved in Blogging (if you want your work to be preserved beyond your lifespan)",
  "url": "https://eve.gd/2026/04/19/the-necessary-pain-involved-in-blogging-if-you-want-your-work-to-be-preserved-beyond-your-lifespan/",
  "datePublished": "2026-04-19",
  "inLanguage": "en-GB",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "author": {
    "@type": "Person",
    "name": "Martin Paul Eve",
    "@id": "https://orcid.org/0000-0002-5589-8511",
    "identifier": "https://orcid.org/0000-0002-5589-8511"
  },
  "isPartOf": {
    "@type": "Blog",
    "name": "eve.gd: Martin Paul Eve",
    "url": "https://eve.gd"
  }
}
```

I can also do this for DOIs. Say I want to cite an academic article (I will [use one of mine for now](https://doi.org/10.31274/jlsc.16288)) I can just use:

- https://doi.org/10.31274/jlsc.16288

and it will produce 

I will continue to improve the infrastructure of my blog in this way; it adds credence to the site, as well as helping with [the preservation effort I detailed before](/2026/04/19/the-necessary-pain-involved-in-blogging-if-you-want-your-work-to-be-preserved-beyond-your-lifespan/).

Finally, in [the Zotero post](https://eve.gd/2026/06/23/making-blog-posts-harvestable-by-zotero-and-preserving-case-in-citation-fields/), I made reference to Tom Elliott's blog being defunct. Which it does seem to be. But he continues to have an online presence, on [Mastodon](https://hcommons.social/@paregorios), [Bluesky](https://bsky.app/profile/paregorios.bsky.social), and the [web itself](https://pleiades.stoa.org/). We had a nice brief correspondence on Bluesky.

