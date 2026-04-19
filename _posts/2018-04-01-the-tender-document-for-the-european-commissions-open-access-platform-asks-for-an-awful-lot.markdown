---
title: "The Tender Document for the European Commission's Open Access Platform Asks for an Awful Lot for Not Very Much"
layout: post
image:
  feature: oa.png
doi: "https://doi.org/10.59348/ncwha-02a74"
archive: "https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2018/04/01/the-tender-document-for-the-european-commissions-open-access-platform-asks-for-an-awful-lot"
---
I've just been reading the [EC’s tender document](https://etendering.ted.europa.eu/cft/cft-document.html?docId=37014) for their new open-access platform. Everyone thinks that it's a shoo-in for F1000. But quite frankly, good luck to whoever gets it. Some comments:

> "Please be aware that after the UK's withdrawal from the EU, the rules of access to EU procurement procedures of economic operators [...] will apply [...]. In case such access is not provided by legal provisions in force, candidates or tenderers from the UK could be rejected."

Just noting that the clear "Brexit advantage" is showing here. Thanks to my fellow country-people for this.

> “The technological solution shall deliver the services described in the present tender specifications without noticeable delay for all categories of users continually and with 99.999% per year uptime.”

OK, wait, what? This is a [higher uptime requirement than achieved by Amazon](https://www.quora.com/Does-Amazon-EC2-have-an-uptime-guarantee-Do-they-have-SLA-Can-it-be-used-for-a-production-environment-for-a-site-that-needs-to-be-up-most-of-the-time). The platform cannot be offline for more than 5 minutes over the course of an entire year. This is total overkill, in my view, for a scholarly communications platform.

> “The Platform shall be highly responsive to increased levels of traffic and the user interface must be ready to receive at minimum of 10,000 (ten thousand) individual user sessions per day with a standard response time of one second and receive at peak levels a minimum 5,000 (five thousand) individual user sessions per second with a response time of no more than two seconds.”

This is a very heavy requirement. It will require multiple distributed redundant servers on a scalable computing infrastructure running Varnish Cache. The sysadmin burden of maintaining these is high and needs to be staffed appropriately on a 24hr a day basis.

> “The Platform must offer content syndication functionalities and automatic transfer of peer-reviewed publications into author-designated institutional, subject or other repositories that are listed in the directory of open access repositories”

This is a painful technological task that, as far as I know, has not yet been successfully achieved by any platform. There are all sorts of permissions issues with pushing to arbitrary repositories and the SWORD protocol is pretty hard to get right.

> “All publications and pre-prints will be licensed by authors with Creative Commons licenses CC-BY or CC0, or equivalent standard open and machine-readable licenses, in such a manner that search engines can identify the publications as such.”

This is going to go down badly in some disciplines where third-party material/re-use is common.

> “Document the business model (processes, actors and costs) of the operation of the Platform as a publishing service as part of the sustainability deliverables.”

OK, so the EC also want the tender to develop a business model to run the platform in perpetuity after the four-year period, presumably sticking to the non-APC model. Good luck with that.

> “The Contractor will be fully transparent regarding the costing of services overall and on a per-article basis to the European Commission, as well as to the public.”

So, the Commission insists that there be no article processing charges for authors, but it still wants a breakdown of costs by article.

> “The Contractor will not charge the Commission for different versions of the same article.”

This is interesting. So: a preprint is posting a PDF, LaTeX or similar version online (trivial). The final article is required to be in XML, PDF, and HTML forms, though. Creating the XML, in particular, is extremely heavy work that usually uses sub-contractors. If you were to make this work economically, you’d have to pre-budget typesetting costs into your preprint costs.

> “ensure uptake of the Platform through a dedicated communication campaign at the beginning of the contract implementation and ongoing communication activities for the entire duration of the contract implementation.”

The tenderer also needs a member of staff dedicated to marketing.

The reporting requirements, in general, in the tender are _extremely_ heavy.

> “The annual turnover of the last two financial years must be above EUR 1 000 000; this criterion applies to the tenderer as a whole, i.e. the combined capacity of all members of a group in case of a joint tender.”

This seriously restricts the entities that can apply.

The team requirements for the project are huge:

> Profile 1: a project/business manager (over ten years of experience) in relevant services, with experience in open access publishing;
> Profile 2: handling editors (senior, over 5 years of experience and junior, between 2-5 years of experience);
> Profile 3: certified IT developers and IT support (senior and junior, as above);
> Profile 4: certified software engineer (at least 2 years of experience);
> Profile 5: metadata specialist/librarian (at least 2 years of experience);
> Profile 6: communications experts (senior and junior, as above).

That is a large staff base.

Well, surely they'll give a lot of money for it?

>“An indicative estimation of the cost of these tasks is 1 000 000 euros for the duration of the Framework Contract, i.e. for 4 (four) years”.

For a platform handling 5,600 articles that is only allowed 5 minutes of downtime per year and must load within a second at any point (see below). This gives you 250,000 per year for project management, business staff, tech staff, and communications staff. A good member of tech staff -- of which you're going to need more than one for 24hr per day coverage -- is going to cost you at least 70k EUR per year. So let's say you have two and that takes you to 140k EUR. You then have 110k EUR left per year to develop the business models (marketing + management), handle reporting (which is really heavy), oversee the entire operation, conduct the communications campaign, file accounts, handle legal etc. etc.

Indeed, I cannot see how it is economically viable to deliver the platform requirements that they have, without cross-subsidising from the per-article charges, although these are supposed to represent purely "production costs". As before: good luck to whoever gets it!





