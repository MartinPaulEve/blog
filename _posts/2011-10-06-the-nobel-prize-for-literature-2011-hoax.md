---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2011/10/06/the-nobel-prize-for-literature-2011-hoax
categories:
- Technology
- Literature
comments:
- author: Profadamroberts
  author_email: profadamroberts@gmail.com
  author_url: ''
  content: It fooled me!
  date: 2011-10-06 11:17:00 +0200
  date_gmt: 2011-10-06 11:17:00 +0200
  id: 6544
date: 2011-10-06 11:15:19 +0200
date_gmt: 2011-10-06 11:15:19 +0200
doi: https://doi.org/10.59348/ygq5n-mjc47
layout: post
published: true
status: publish
tags:
- Literature
- nobel
- hoax
title: The Nobel Prize for Literature 2011 Hoax
wordpress_id: 1525
wordpress_url: https://www.martineve.com/?p=1525
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mjtmvdc2s"
---

<p>About half an hour before the official announcement of the Nobel Prize for Literature, 2011 (which was awarded to Tomas Tranströmer) reports started circulating on Twitter that the winner was, controversially, the Serbian author, Dobrica Cosic. The source was <a href="http://www.nobelprizeliterature.org">http://www.nobelprizeliterature.org</a>, which looked like this:</p>
<p><img src="https://www.martineve.com/wp-content/uploads/2011/10/Serb-1024x539.png" alt="Fake Nobel announcement" title="Fake Nobel announcement" style="width:750px;" class="alignnone size-large wp-image-1526" /></p>
<p>Smelling a rat, as the official site is nobelprize.org, I decided to check it out.</p>
<p>The first result was a probe from the Linux DNS lookup utility, dig, which revealed the following differences between the sites:</p>

{% highlight bash %}
martin@allusion:~$ dig nobelprizeliterature.org

; <<>> DiG 9.7.3 <<>> nobelprizeliterature.org
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 3516
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 3, ADDITIONAL: 3

;; QUESTION SECTION:
;nobelprizeliterature.org.	IN	A

;; ANSWER SECTION:
nobelprizeliterature.org. 14400	IN	A	67.205.43.34

;; AUTHORITY SECTION:
nobelprizeliterature.org. 86265	IN	NS	ns2.dreamhost.com.
nobelprizeliterature.org. 86265	IN	NS	ns1.dreamhost.com.
nobelprizeliterature.org. 86265	IN	NS	ns3.dreamhost.com.

;; ADDITIONAL SECTION:
ns1.dreamhost.com.	8989	IN	A	66.33.206.206
ns2.dreamhost.com.	7503	IN	A	208.96.10.221
ns3.dreamhost.com.	7485	IN	A	66.33.216.216

;; Query time: 183 msec
;; SERVER: 10.8.0.1#53(10.8.0.1)
;; WHEN: Thu Oct  6 11:56:24 2011
;; MSG SIZE  rcvd: 173

martin@allusion:~$ dig nobelprize.org

; <<>> DiG 9.7.3 <<>> nobelprize.org
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 27771
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;nobelprize.org.			IN	A

;; ANSWER SECTION:
nobelprize.org.		3505	IN	A	130.242.18.28

;; Query time: 29 msec
;; SERVER: 10.8.0.1#53(10.8.0.1)
;; WHEN: Thu Oct  6 11:56:29 2011
;; MSG SIZE  rcvd: 48
{% endhighlight %}

<p>As is clear, the latter, authentic site is running on it's own independent IP address, while the former points to the commercial web host provider Dreamhost.</p>
<p>Secondly, here's a comparison of the DNS whois responses for the two domains. Firstly, for the fake entry:</p>

{% highlight bash %}
martin@allusion:~$ whois nobelprizeliterature.org
NOTICE: Access to .ORG WHOIS information is provided to assist persons in 
determining the contents of a domain name registration record in the Public Interest Registry
registry database. The data in this record is provided by Public Interest Registry
for informational purposes only, and Public Interest Registry does not guarantee its 
accuracy.  This service is intended only for query-based access.  You agree 
that you will use this data only for lawful purposes and that, under no 
circumstances will you use this data to: (a) allow, enable, or otherwise 
support the transmission by e-mail, telephone, or facsimile of mass 
unsolicited, commercial advertising or solicitations to entities other than 
the data recipient's own existing customers; or (b) enable high volume, 
automated, electronic processes that send queries or data to the systems of 
Registry Operator or any ICANN-Accredited Registrar, except as reasonably 
necessary to register domain names or modify existing registrations.  All 
rights reserved. Public Interest Registry reserves the right to modify these terms at any 
time. By submitting this query, you agree to abide by this policy. 

Domain ID:D163518199-LROR
Domain Name:NOBELPRIZELITERATURE.ORG
Created On:05-Oct-2011 15:13:54 UTC
Last Updated On:05-Oct-2011 16:42:08 UTC
Expiration Date:05-Oct-2012 15:13:54 UTC
Sponsoring Registrar:Directi Internet Solutions Pvt. Ltd. d/b/a PublicDomainRegistry.com (R27-LROR)
Status:CLIENT TRANSFER PROHIBITED
Status:TRANSFER PROHIBITED
Status:ADDPERIOD
Registrant ID:DI_18210988
Registrant Name:Gjord Halvorsen
Registrant Organization:NPABL
Registrant Street1:Brynjulf Bulls Plass 1
Registrant Street2:
Registrant Street3:
Registrant City:Oslo
Registrant State/Province:Oslo
Registrant Postal Code:0124
Registrant Country:NO
Registrant Phone:+49.301000
Registrant Phone Ext.:
Registrant FAX:
Registrant FAX Ext.:
Registrant Email:hgjorn@yahoo.com
Admin ID:DI_18210988
Admin Name:Gjord Halvorsen
Admin Organization:NPABL
Admin Street1:Brynjulf Bulls Plass 1
Admin Street2:
Admin Street3:
Admin City:Oslo
Admin State/Province:Oslo
Admin Postal Code:0124
Admin Country:NO
Admin Phone:+49.301000
Admin Phone Ext.:
Admin FAX:
Admin FAX Ext.:
Admin Email:hgjorn@yahoo.com
Tech ID:DI_18210988
Tech Name:Gjord Halvorsen
Tech Organization:NPABL
Tech Street1:Brynjulf Bulls Plass 1
Tech Street2:
Tech Street3:
Tech City:Oslo
Tech State/Province:Oslo
Tech Postal Code:0124
Tech Country:NO
Tech Phone:+49.301000
Tech Phone Ext.:
Tech FAX:
Tech FAX Ext.:
Tech Email:hgjorn@yahoo.com
Name Server:NS1.DREAMHOST.COM
Name Server:NS2.DREAMHOST.COM
Name Server:NS3.DREAMHOST.COM
Name Server: 
Name Server: 
Name Server: 
Name Server: 
Name Server: 
Name Server: 
Name Server: 
Name Server: 
Name Server: 
Name Server: 
DNSSEC:Unsigned
{% endhighlight %}

<p>whereas the official site is registered thus:</p>

{% highlight bash %}
martin@allusion:~$ whois nobelprize.org
NOTICE: Access to .ORG WHOIS information is provided to assist persons in 
determining the contents of a domain name registration record in the Public Interest Registry
registry database. The data in this record is provided by Public Interest Registry
for informational purposes only, and Public Interest Registry does not guarantee its 
accuracy.  This service is intended only for query-based access.  You agree 
that you will use this data only for lawful purposes and that, under no 
circumstances will you use this data to: (a) allow, enable, or otherwise 
support the transmission by e-mail, telephone, or facsimile of mass 
unsolicited, commercial advertising or solicitations to entities other than 
the data recipient's own existing customers; or (b) enable high volume, 
automated, electronic processes that send queries or data to the systems of 
Registry Operator or any ICANN-Accredited Registrar, except as reasonably 
necessary to register domain names or modify existing registrations.  All 
rights reserved. Public Interest Registry reserves the right to modify these terms at any 
time. By submitting this query, you agree to abide by this policy. 

Domain ID:D2213820-LROR
Domain Name:NOBELPRIZE.ORG
Created On:17-Oct-1998 04:00:00 UTC
Last Updated On:19-Jul-2011 12:19:42 UTC
Expiration Date:16-Oct-2013 04:00:00 UTC
Sponsoring Registrar:Domaininfo AB, aka domaininfo.com (R29-LROR)
Status:CLIENT TRANSFER PROHIBITED
Registrant ID:DI-235-THE
Registrant Name:Domain Name Department
Registrant Organization:The Nobelfoundation
Registrant Street1:c/o Dipcon AB, William Gibsons vag 1
Registrant Street2:
Registrant Street3:
Registrant City:Jonsered
Registrant State/Province:
Registrant Postal Code:43376
Registrant Country:SE
Registrant Phone:+46.317202030
Registrant Phone Ext.:
Registrant FAX:+46.317202039
Registrant FAX Ext.:
Registrant Email:dms@dipcon.com
Admin ID:DI-13-DEP
Admin Name:Domain Name Department
Admin Organization:Dipcon AB
Admin Street1:William Gibsons vag 1
Admin Street2:
Admin Street3:
Admin City:Jonsered
Admin State/Province:
Admin Postal Code:43376
Admin Country:SE
Admin Phone:+46.317202030
Admin Phone Ext.:
Admin FAX:+46.317202039
Admin FAX Ext.:
Admin Email:dms@dipcon.com
Tech ID:DI-13-DEP
Tech Name:Domain Name Department
Tech Organization:Dipcon AB
Tech Street1:William Gibsons vag 1
Tech Street2:
Tech Street3:
Tech City:Jonsered
Tech State/Province:
Tech Postal Code:43376
Tech Country:SE
Tech Phone:+46.317202030
Tech Phone Ext.:
Tech FAX:+46.317202039
Tech FAX Ext.:
Tech Email:dms@dipcon.com
Name Server:SUNIC.SUNET.SE
Name Server:NS.NOBEL.SE
Name Server: 
Name Server: 
Name Server: 
Name Server: 
Name Server: 
Name Server: 
Name Server: 
Name Server: 
Name Server: 
Name Server: 
Name Server: 
DNSSEC:Unsigned
{% endhighlight %}

<p>While there is no guarantee that the information is genuine, journalists who wanted to pursue this further would only have to investigate this information on the registrant of the fake domain name:</p>
<p>Gjord Halvorsen<br />
Brynjulf Bulls Plass 1<br />
Oslo<br />
0124<br />
Norway<br />
+49.301000<br />
hgjorn@yahoo.com</p>

<p>The registrant has used the address of the official committee, so that's of no use. The name could, also, be fake. The only thing that would, probably need to be real there would be the email address.</p>