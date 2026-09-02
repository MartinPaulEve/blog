---
archive: https://wayback.archive-it.org/22123/20241101171236/https://eve.gd/2025/12/03/error-failed-to-build-failed-to-solve-failed-to-compute-cache-key-failed-to-calculate-checksum-of-ref-xxyyzz/
date: 2025-12-03
doi: https://doi.org/10.59348/1r757-mm685
roguescholar: https://rogue-scholar.org/records/0vav7-jkm46
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lvphq3z2h
image:
  feature: header_geek.png
layout: post
ogImage: images/header_geek.png
title: 'ERROR: failed to build: failed to solve: failed to compute cache key: failed
  to calculate checksum of ref XXYYZZ'
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lvphq3z2h"
categories:
- Programming
kcworks: https://works.hcommons.org/records/0hfs1-msn69
---

Another annoying error that you can get, during a docker build, that basically does not explain what's going on is something like:

	Dockerfile.php:73
	--------------------
	  71 |     RUN mkdir -p /app/site/web && chown www-data:www-data /app/site/web
	  72 |     COPY --chown=www-data:www-data ./scripts /app/scripts
	  73 | >>> COPY --chown=www-data:www-data ./site/web/*.* /app/site/web/
	  74 |     COPY --chown=www-data:www-data ./plugins /app/plugins
	  75 |     COPY --chown=www-data:www-data ./mu-plugins /app/mu-plugins
	--------------------
	ERROR: failed to build: failed to solve: failed to compute cache key: failed to calculate checksum of ref 3d713212-c67a-44e0-bee9-d62fb272cc6d::qhwfoyzlhjy0i7wvs60xthwk1: "/site/web/phpinfo.php": not found

This error does, actually, tell you which file it's having a problem with. See the end of the last line. Here it says that /site/web/phpinfo.php was not found. But when I look in /site/web/ there is an entry for phpinfo.php.

So what's happening?

It turns out that the problem here is a missing symbolic link. That is, the file phpinfo.php has been linked, but the target does not exist. So phpinfo.php's symbolic link does not resolve correctly.

The solution is simply to delete such a file or to make the symbolic link resolve correctly.