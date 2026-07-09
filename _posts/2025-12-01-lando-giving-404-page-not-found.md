---
archive: https://wayback.archive-it.org/22123/20241101171236/https://eve.gd/2025/12/02/lando-giving-404-page-not-found/
date: 2025-12-01
doi: https://doi.org/10.59348/6k713-x2m53
image:
  feature: header_geek.png
layout: post
ogImage: header_geek.png
title: Lando giving '404 page not found'
---

I spent the morning bashing my head against a brick wall, trying to sort out a problem with my Lando install. This worked on Friday, but by Monday was misbehaving. I hadn't touched the codebase, but every time I hit the primary URL, I got: "404 page not found".

I could see that my nginx server was running on https://localhost:32840. When I visited this, I could see that I was connecting to WordPress on nginx directly (it gave me a database connection error, because the URL wasn't recognised.) But https://commons-wordpress.lndo.site/, my main Lando URL, was just giving the dreaded 404 error.

This is because the main traefik proxy that Lando uses *was out of date compared to my docker version*. I had updated docker recently and the two had fallen out of sync.

The solution was frustratingly obvious and you can check if this is your problem by running:

	docker logs -f landoproxyhyperion5000gandalfedition_proxy_1

If you get something like:

	time="2025-12-01T14:22:27Z" level=error msg="Provider connection error Error response from daemon: client version 1.24 is too old. Minimum supported API version is 1.44, please upgrade your client to a newer version, retrying in 11.996919148s" providerName=docker

then you need to run:

	lando update

... and that's it. Urgh.