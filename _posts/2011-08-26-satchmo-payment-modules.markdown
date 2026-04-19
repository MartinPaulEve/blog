---
layout: post
image: 
    feature: geek.png
status: publish
published: true
title: Satchmo payment modules
wordpress_id: 1423
wordpress_url: https://www.martineve.com/?p=1423
date: !binary |-
  MjAxMS0wOC0yNiAxMzo1MDoxMyArMDIwMA==
date_gmt: !binary |-
  MjAxMS0wOC0yNiAxMzo1MDoxMyArMDIwMA==
categories:
- Technology
- Django
tags:
- django
- satchmo
- programming
comments: []
doi: "https://doi.org/10.59348/24gab-zkb92"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/08/26/satchmo-payment-modules"
---
<p>I've been working, over the past few days, on a web store for a client using Satchmo. I wanted to share some of my findings here so that others don't trip up at the same places. </p>
<p>Firstly, <a href="https://bitbucket.org/MartinEve/satchmo_variation_image">I've committed a fix</a> that has been pulled into the mainline build which puts images from product variations into a JSON array on the product view page. This means, with suitable template modifications, that you can display alternate images based on which variation is selected - a green t-shirt for example. </p>
<p>Secondly, I've been working through the payment plugin, trying to find a suitable module. Things of which you need to be aware:</p>
<ul>
<li>Using the sagepay module requires you to have the relevant certification for safe storage of credit card details. It is using the "direct" API mode.</li>
<li>Using the authorize.net module has a similar requirement, as it is using the "AIM" API mode.</li>
<li>Using the Google Checkout module requires you to have an SSL certificate for your domain as it uses method 3 of the notification callback modes -- html. There seem to be several bugs in this module to do with clearing the cart when the user returns. I hope to have a fix committed for this shortly and it will be available <a href="https://bitbucket.org/MartinEve/satchmo_google_checkout">at my bitbucket</a>. You'll also need to enable "WSGIPassAuthorization On" in your vhost config file.</li>
</ul>
<p>Anyway, I hope that saves someone some effort and will update on my progress. </p>
<p>On a final note: I wrote this entire blog post on my new Samsung Galaxy S2 using the SwiftKey keyboard and I'm pretty sure it was no slower than typing it on my PC.</p>
<p><i>Featured image by <a href="http://www.flickr.com/photos/teleniek0/">teleniek0</a> under a CC-BY-SA license.</i></p>





