---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2012/07/11/starting-an-open-access-journal-a-step-by-step-guide-part-2
categories:
- Open Access
- Publishing Technology
comments: []
date: 2012-07-11 09:21:11 +0200
date_gmt: 2012-07-11 09:21:11 +0200
doi: https://doi.org/10.59348/y45ka-p7z83
roguescholar: https://rogue-scholar.org/records/g0gxx-8vg61
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mib7bqa2o
image:
  feature: oa.png
layout: post
ogImage: images/oa.png
published: true
status: publish
tags:
- Open Access
- Publishing
title: 'Starting an Open Access Journal: a step-by-step guide part 2'
wordpress_id: 2189
wordpress_url: https://eve.gd/?p=2189
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mib7bqa2o"
kcworks: https://works.hcommons.org/records/t1g1f-p3v43
references:
- title: OJS User Guide
  type: TechArticle
  url: http://pkp.sfu.ca/ojs/docs/userguide/2.3.3/index.html
  isPartOf:
    name: PKP Docs
    type: WebSite
- title: OJS Installation Instructions
  type: TechArticle
  url: http://pkp.sfu.ca/ojs/docs/userguide/2.3.3/systemAdministrationInstallation.html
  isPartOf:
    name: PKP Docs
    type: WebSite
- title: Requesting an ISSN
  type: WebPage
  url: http://www.issn.org/2-22652-Requesting-an-ISSN.php
  isPartOf:
    name: ISSN
    type: WebSite
- https://www.pynchon.net/owap/article/view/38 # Orbit journal article 38 on pynchon.net
- title: Crossref fees
  type: WebPage
  url: http://www.crossref.org/02publishers/20pub_fees.html
  isPartOf:
    name: Crossref
    type: WebSite
- title: Home
  type: WebPage
  url: http://oaspa.org/
  isPartOf:
    name: OASPA
    type: WebSite
- title: LOCKSS Program
  type: WebSite
  url: http://www.lockss.org/
- http://dx.doi.org/10.7766/orbit.v1.1.38 # DOI link to Orbit journal article 38
---

<p>Following on from <a href="https://eve.gd/2012/07/10/starting-an-open-access-journal-a-step-by-step-guide-part-1/">Part 1</a>, let's begin to talk about the technological side of starting an OA journal.</p>
<p><img src="https://eve.gd/wp-content/uploads/2012/07/file0001748951237-1024x745.jpg" alt="A book" title="A book" style="width:750px;" class="alignnone size-large wp-image-2190" /></p>
<p>There are several components to the system that all need to come together. The timescales for ensuring this happens are different, but here's some descriptions and estimates on the different components.</p>
<p><b>Open Journal Systems</b><br />
OJS is a free, open source platform developed by the Public Knowledge Project that is designed to get you off the ground quickly. Pre-requistites are:</p>
<ul>
<li>A web server</li>
<li>PHP support on said server</li>
<li>MySQL database support (or another supported DB)</li>
<li>Permission for web applications to write to the filesystem on the server</li>
</ul>
<p>The document you need to read, and understand, to fully get OJS is their <a href="http://pkp.sfu.ca/ojs/docs/userguide/2.3.3/index.html">Userguide</a>. For this specific part of the installation, you'll want to follow their <a href="http://pkp.sfu.ca/ojs/docs/userguide/2.3.3/systemAdministrationInstallation.html">installation instructions</a>. I can get an OJS box up and running in 45 minutes or so. For a first time user with moderate technical competence, budget in a fair few hours.</p>
<p><b>ISSN number</b><br />
To get an ISSN number, which is crucial for your journal (and is also free of charge!), you need to apply to the <a href="http://www.issn.org/2-22652-Requesting-an-ISSN.php">relevant ISSN provider for your country</a>. In the UK, this is the <a href="http://www.bl.uk/bibliographic/issn.html">British Library</a>. The turnaround time on this varies, but is often quicker than the two months they stipulate.</p>
<p><b>DOI numbers</b><br />
Right, this is where it can get a bit complicated. DOI (Document Object Identification/Identifier) numbers are part of a system that ensures that articles are permanently active. Let's take an example. The following is a DOI resolver URL:</p>
<p><a href="http://dx.doi.org/10.7766/orbit.v1.1.38">http://dx.doi.org/10.7766/orbit.v1.1.38</a></p>
<p>The number is composed of a prefix (10.7766), which is my publisher prefix, and a suffix (orbit.v1.1.38). Together these form a unique string that identify the article Eve, Martin, Samuel Thomas, Doug Haynes, & Simon de Bourcier. "Preface." <i>Orbit: Writing Around Pynchon</i> [Online], 1.1 (2012): n. pag. Web. 10 Jul. 2012.</p>
<p>So, when you visit the DOI resolver URL above, it points you over to <a href="https://www.pynchon.net/owap/article/view/38">https://www.pynchon.net/owap/article/view/38</a>, which is the journal hosted on my server. Let us assume that something happens to me or my finances. For example, I can no longer pay for my server, or I get run over by a bus (I'm hoping to postpone both of these occurrences). The archival service for the journal will notice a "trigger event" that authorises them to release, forever, the material on the journal. The DOI number can then be updated to point to the archives copy and, tada, the material has then been preserved even in the case of catastrophe or fold. I hope it's clear, from this, the important role that DOI numbers play.</p>
<p>As a member of CrossRef, assigning DOIs, you have legal obligations in the contract. You must:</p>
<ul>
<li>Assign DOIs to all your articles</li>
<li>Ensure you never assign the same DOI more than once</li>
<li>Ensure that DOIs always resolve to the correct article</li>
<li>Ensure that, if you move hosts/addresses, you update the metadata so that the DOI resolves</li>
<li>Give the DOI link of any article that has a DOI number assigned in an article's citations</li>
<li>Deposit metadata and DOI information in a timely fashion to CrossRef</li>
</ul>
<p>This is all easily doable via OJS built-in mechanisms, but it is a legal contract, so not to be taken lightly or ignored.</p>
<p>CrossRef, the registration organisation for DOIs on scholarly or research material, have <a href="http://www.crossref.org/02publishers/20pub_fees.html">various levels of fees</a>. The reason for this is, once again, that they need ways to <b>force</b> publishers to keep their links up-to-date and to deposit material. Financial sanctions have proved the most effective way of doing this.</p>
<p>However, for the journal that is attempting to evade the fee-paying structures of commercial OA enterprises, this is little consolation. Never fear. <a href="http://oaspa.org/">The Open Access Scholarly Publishers Association</a> has a deal with CrossRef for scholar-publisher members (that's you, as an individual) that means that the OASPA will allow you to get a DOI prefix and assign up to 50 DOIs inclusive of their membership fee, which is a much more reasonable 75 euros. In my case, because I hadn't started the journal at that point, I was signed up as a non-voting member of OASPA, but this certainly helped.</p>
<p>Timescale-wise, my application to OASPA took much longer than usual (I am told) because CrossRef were in the process of updating their member agreement. I signed up on the 16th April and was ready to go by the 7th July. So budget in three months.</p>
<p><b>CLOCKSS</b></p>
<p><a href="http://www.clockss.org/clockss/Home">CLOCKSS</a> is the archival service that I have chosen to use for my journal. Based upon the <a href="http://www.lockss.org/">LOCKSS system</a>, CLOCKSS stands for Controlled Lots of Copies Keeps Stuff Safe. The principle here is that your articles are stored on multiple servers, spread across the globe. In the event of a trigger, CLOCKSS will release the material. Again, there's a fee ($200/year). I am unable to comment on timescales as I have yet to be fully set up here, but as I only applied three days ago, this doesn't seem so surprising so far.</p>
<p>Again, I'm going to stop writing here so that I can get on with some other work, but in the next section I'll begin to detail some of the options available in OJS and how the process works.</p>
<p><a href="https://eve.gd/2012/07/12/starting-an-open-access-journal-a-step-by-step-guide-part-3/">Part 3 &gt;&gt;</a></p>