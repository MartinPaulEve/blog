---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2015/12/14/auto-renewing-ssl-certificates-with-letsencrypt
categories:
- tech
- SSL
date: 2015-12-14
doi: https://doi.org/10.59348/8gw4g-s2z59
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
tags:
- tech
- SSL
title: Auto-renewing SSL Certificates with Let'sEncrypt
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mbzilnv2e"
---

[Let'sEncrypt](http://letsencrypt.org/) is a brilliant new service that aims to bring mass-scale SSL, free-of-charge to the wide web. It's in beta at the moment but it works pretty well. In fact, this site is secured with it!

I wanted to quickly give some guidance on how to setup automatic renewal of certificates on a Linux box for those who wish to do so. The base requirement is that you've got Let'sEncrypt working to the extent that your Apache setup is using the certificate that it generates.

Step 1 is to put the following in a file called cli.ini inside your Let'sEncrypt directory:

        # This is an example of the kind of things you can do in a configuration file.
        # All flags used by the client can be configured here. Run Let's Encrypt with
        # "--help" to learn more about the available options.

        # Use a 4096 bit RSA key instead of 2048
        rsa-key-size = 4096

        server = https://acme-v01.api.letsencrypt.org/directory

        # Uncomment and update to register with the specified e-mail address
        email = your@email.com

        # Uncomment and update to generate certificates for the specified
        # domains.
        domains = www.domain.com, domain.com

        # Uncomment to use a text interface instead of ncurses
        text = True

        # Uncomment to use the standalone authenticator on port 443
        authenticator = apache

You should change the "domains" aand "email" line, as appropriate, for your site.

Step 2 is to run the following command:

./letsencrypt-auto --renew -c cli.ini certonly

If this works then you won't be prompted to enter any information by hand and the process will silently complete. Then check your live site and see if the certificate has been renewed. If it has, then you can add this line to your Crontab to run every 30 days (once per month).