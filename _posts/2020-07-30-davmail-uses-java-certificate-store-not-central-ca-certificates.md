---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2020/07/30/davmail-uses-java-certificate-store-not-central-ca-certificates
date: 2020-07-30
doi: https://doi.org/10.59348/p45j7-fjr65
layout: post
title: davmail uses Java certificate store, not central ca-certificates
---

A note to self (and others) for when this problem happens again. My university today updated the certificate for their OWA webmail service, signed by a certificate authority that I did not have in my trust chain.

This triggers the following error in DavMail: "java.security.cert.CertificateException: User rejected certificate".

In order to fix it, you need to install the certs into the _Java_ keystore, which is different to the central ca-certificates package on Debian.

So, use Firefox or similar to download the PEM files (authority + chain), then do the following in a bash script:

"for file in *.pem; do openssl x509 -outform der -in "$file" -out /tmp/certificate.der; keytool -import -alias "$file" -keystore ./java/cacerts -file /tmp/certificate.der -deststorepass changeit -noprompt; done;"