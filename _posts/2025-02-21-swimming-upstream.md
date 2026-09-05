---
archive: https://wayback.archive-it.org/22123/20241101171236/https://eve.gd/2025/02/21/swimming-upstream
date: 2025-02-21
doi: https://doi.org/10.59348/3e3vq-jf273
roguescholar: https://rogue-scholar.org/records/adtdm-14j28
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lw4afg22h
image:
  feature: header_fish.png
layout: post
ogImage: images/header_fish.png
title: Swimming upstream
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lw4afg22h"
categories:
- Scholarly Communications
- Programming
kcworks: https://works.hcommons.org/records/8gvmt-0he56
references:
- https://www.zdnet.com/article/dumping-open-source-for-proprietary-rarely-pays-off-better-to-stick-a-fork-in-it/ # ZDNet: forking open source vs proprietary software
- https://github.com/inveniosoftware/pytest-invenio/issues/114 # Ian's pytest-invenio test framework fix, GitHub issue
- https://github.com/inveniosoftware/invenio-saml/pull/48 # Ian's invenio-saml SAML user matching pull request
---

Open source projects like InvenioRDM -- on which we rely for our repository software at Knowledge Commons -- thrive on community contributions. When initiatives like ours not only use these platforms but actively contribute improvements back to the original codebase, everyone benefits. This "upstreaming" process takes work, but it represents the collaborative spirit that makes open source software so powerful. My colleague, Ian, who is our repository developer has, in the past day, contributed a set of fixes back to Invenio, which should improve the software for everyone.

First, for those who are not so techy, what is "upstreaming"? Upstreaming refers to the practice of contributing locally-developed improvements back to the original open-source project. Rather than keeping customizations isolated within our own implementation, these enhancements are shared with the broader community and make it back to the project from which they derived. In a world where we are [encouraged to fork all the time](https://www.zdnet.com/article/dumping-open-source-for-proprietary-rarely-pays-off-better-to-stick-a-fork-in-it/) and just maintain our changes locally, upstreaming represents the collaborative compromise.

Recently, as I say, our colleague Ian made two significant contributions to InvenioRDM. His work inspired this reflection on the importance of upstream contributions in the open source ecosystem. Ian's willingness to share these changes with the wider Invenio community exemplifies the collaborative approach for which we are aiming.

[The first of Ian's changes](https://github.com/inveniosoftware/pytest-invenio/issues/114) is very technical, but essentially: unit and integration tests are key to developing robust software. Ian found a bug in the "teardown" portion of Invenio's test framework and has submitted a new pull request to fix this.

[The second contribution](https://github.com/inveniosoftware/invenio-saml/pull/48) is really key to us: we need to be able to match up users who login to Invenio with users across the rest of the platform. This pull request allows you to specify a function (a "callable") to perform this lookup, rather than hardcoding it. This brings users flexibility to integrate Invenio into their own ecosystems.

Why do this?

### Reduces technical debt
When customizations remain solely in your local implementation, each upstream update requires reconciling conflicts between your modifications and the main codebase. By contributing changes upstream, Knowledge Commons maintains closer alignment with the main project trajectory.

### Community Recognition
We hope that contributing to open source projects establishes us as a valued community member.

### Improved Software Quality

Upstream contributions undergo a form of peer/code review, helping to identify potential issues before they impact anyone's production environment. This collaborative refinement process results in more robust code.

### Shared Maintenance Burden

When your features exist in the main codebase, the entire community helps to maintain them. The Knowledge Commons team no longer bears sole responsibility for ensuring compatibility with future updates and, even if we ceased to exist (I hope not!) the work we did will live on, for others to use.

We hope that Knowledge Commons demonstrates how academic initiatives can be not just consumers of open source software, but active contributors to its evolution. Ian's recent contributions exemplify this collaborative approach, which strengthens both our implementation and the broader InvenioRDM ecosystem. Sure, these are small contributions, but I hope that they exemplify our approach to re-using code from other projects. By continuing to upstream our improvements, we ensure Knowledge Commons remains sustainable while simultaneously elevating the software on which we depend.