---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2022/05/07/static-site-hosting-in-the-cloud-should-not-be-this-hard-in-2022
date: 2022-05-07
doi: https://doi.org/10.59348/9x33x-1ky82
roguescholar: https://rogue-scholar.org/records/s7pj5-2v205
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lz6isj42h
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
title: Static site hosting in the cloud should not be this hard in 2022
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lz6isj42h"
categories:
- Programming
kcworks: https://works.hcommons.org/records/sqv2m-j7y54
references:
- title: Cloudcraft – Draw AWS diagrams
  type: WebSite
  url: https://app.cloudcraft.co/
  isPartOf:
    name: Cloudcraft
    type: WebSite
- title: 'GitHub - MartinPaulEve/meve-iac: The terraform files to provision eve.gd'
  type: SoftwareSourceCode
  url: https://github.com/MartinPaulEve/meve-iac
  isPartOf:
    name: GitHub
    type: WebSite
- date: '2017-10-18'
  title: Implementing Default Directory Indexes in Amazon S3-backed Amazon CloudFront Origins Using Lambda@Edge
  type: BlogPosting
  url: https://aws.amazon.com/blogs/compute/implementing-default-directory-indexes-in-amazon-s3-backed-amazon-cloudfront-origins-using-lambdaedge/
  isPartOf:
    name: Amazon Web Services Blog
    type: Blog
- title: meve-iac/modules/terraform-aws-lambda-at-edge at main · MartinPaulEve/meve-iac
  type: SoftwareSourceCode
  url: https://github.com/MartinPaulEve/meve-iac/tree/main/modules/terraform-aws-lambda-at-edge
  isPartOf:
    name: GitHub
    type: WebSite
- https://stackoverflow.com/a/52434219/349003 # Stack Overflow answer on Lambda@Edge event lifecycle
- author: Martin Paul Eve
  title: 'eve.gd: Martin Paul Eve'
  type: WebPage
  url: https://books.eve.gd
  isPartOf:
    name: eve.gd
    type: WebSite
---

Last weekend I converted my website hosting to an infrastructure-as-code solution. It's no big deal, I thought. It's just a static site so it must be really easy to provision this. Surely just some kind of AWS S3 bucket associated with a custom domain? I mean, generated static sites are great. They are fast, lightweight, and virtually un-hackable. Surely it must be easy to deploy this?

It turns out that hosting a static site on AWS in 2022 is still somewhat painful. The major problem is that you can't serve directly from an S3 bucket using SSL. This means that you have to setup a Cloudfront distribution in front of your static site. Here's a [cloudcraft.co](https://app.cloudcraft.co/) diagram of [roughly what I came up with](https://github.com/MartinPaulEve/meve-iac).

<img src="/images/StaticSite.png" style="width:100%" alt="Cloud diagram of hosting diagram"/>

Some of the snags I hit along the way:

1. You need a Lambda@Edge function to handle redirects. But not just complex redirects. Even really, really basic redirects. Indeed, Cloudfront won't redirect to index.html inside sub-directories where it exists. The official solution is to [write your own function to handle this](https://aws.amazon.com/blogs/compute/implementing-default-directory-indexes-in-amazon-s3-backed-amazon-cloudfront-origins-using-lambdaedge/). This function has to be located in the us-east-1 region or it won't work, for some reason. So to get basic directory handling, you already have to write some server-side code and work out how to deploy this, which turns out, also, to be [pretty complicated](https://github.com/MartinPaulEve/meve-iac/tree/main/modules/terraform-aws-lambda-at-edge). Debugging these functions is also really difficult, because the Cloudwatch logs replicate to the region where the function ran, not to the region where the function is hosted (which, again, has to be us-east-1). So you end up delving around for ages trying to work out what's going wrong. You need, also, to read and understand the [event lifecycle](https://stackoverflow.com/a/52434219/349003) for Lambda@Edge functions (I needed "origin-request" in the end). This is really not a good solution when, really, you just want is the equivalent of a .htaccess file.

2. Certificate verification is a total pain. I have to manage several SSL certificates because I have subdomains, like [books.eve.gd](https://books.eve.gd). When you verify these, you have to go in and add the DNS entries/click the email verification link. This felt really fragile/breakable.

3. Route 53 management for DNS with Terraform _is_ pretty cool, but it also has loads of snags/gotchas. While most domain registrars and zone hosts use "@" to refer to the root, AWS doesn't. Hence, in Route 53, you don't set the name to "@" but to the domain itself. You also can't add multiple records with the same name -- as you would elsewhere -- but have to set multiple record entries in a single "aws_route53_record".

AWS infrastructure (and Terraform for provisioning) is really flexible. You get a huge amount of control. But, really, this should have been _far_ easier than it was. I just wanted to chuck my static site into an S3 bucket and get it serving. Instead, it turned into a Cloudfront-S3-Lamda@Edge-Route 53-ACM project.