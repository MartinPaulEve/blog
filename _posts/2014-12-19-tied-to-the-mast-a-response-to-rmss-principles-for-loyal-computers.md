---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2014/12/19/tied-to-the-mast-a-response-to-rmss-principles-for-loyal-computers
categories:
- Technology
comments: []
date: 2014-12-19
last_modified_at: 2026-09-06
doi: https://doi.org/10.59348/erzpp-y8227
roguescholar: https://rogue-scholar.org/records/pane5-wzs54
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mdjgljj2u
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- software
title: Tied to the mast? A response to RMS's principles for loyal computers
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mdjgljj2u"
kcworks: https://works.hcommons.org/records/fcspy-znn80
references:
- author: Richard M. Stallman
  title: What Does It Mean for Your Computer to Be Loyal?
  type: WebPage
  url: http://www.gnu.org/philosophy/loyal-computers.html
  isPartOf:
    name: GNU Project - Free Software Foundation
    type: WebSite
- date: '2001-02-05'
  title: Three Laws of Robotics
  type: WebPage
  url: http://en.wikipedia.org/wiki/Three_Laws_of_Robotics
  isPartOf:
    name: Wikipedia
    type: WebSite
---

<p>In a recent essay, Richard M. Stallman, pioneer of the free software movement, asked “<a href="http://www.gnu.org/philosophy/loyal-computers.html">what does it mean for a computer to be loyal?</a>” The "tentative definition" that Stallman outlines consists of: Neutrality towards software; Neutrality towards protocols; Neutrality towards implementations; Neutrality towards data communicated; Debugability; Documentation; and Completeness. I won't, here, reproduce the whole essay as you can read it on the GNU site. What I want to do instead is to point out a few ambiguities and potential sticking points that I identified in the definition here, mostly surrounding the principle of remote attestation.</p>
<h2>Hardware vs. Software</h2>
<p>The first thing that struck me about the "disloyal computer" definition is that although it is generally sound and speaking of hardware, it also seems, at various points, to be speaking about software or the combination of software and hardware. This may not be the intention of the definition. The principles of "neutrality towards software", for example, seem designed to ensure that there is no in-built hardware/firmware signature checking (as in the case of Android smartphones) that will prevent the user from installing whatever operating system or software they would like. The same could be said of some UEFI boot systems ("secure boot").</p>
<p>However, when the piece goes on to talk about remote attestation (i.e. being able to remotely identify which version of software/implementation is being run at the client side), things are, at least to me, a little murkier. Stallman writes:</p>
<blockquote><p>This entails that the computer rejects remote attestation, that is, that it does not permit other computers to determine over the network whether your computer is running one particular software load. Remote attestation gives web sites the power to compel you to connect to them only through an application with DRM that you can't break, denying you effective control over the software you use to communicate with them. Netflix is a notorious example of this.</p></blockquote>
<p>If this is supposed to refer to the hardware level, then great, that's a solid principle. However, the majority of remote attestation implementations are contained within non-free software or in uninspectable remote implementations (hardware + software), Netflix, indeed, being the best example. Is the "computer" in this scenario referring only the hardware or to the whole environment that makes up the computation platform? If hardware runs code as part of its own, integral operation ("firmware"), how does that sit within this definition?</p>
<h2>Design-time vs. Run-time</h2>
<p>The second point, following on from this, that occurs to me is the different points of design in the system. Let us suppose that we designed a loyal hardware system but that the user wishes to run Netflix. In this environment, two of the principles might come into contradiction with each other:</p>
<blockquote><p>The computer will run, without prejudice, whatever software you install in it, and let that software do whatever its code says to do.</p></blockquote>
<blockquote><p>If a computer allows web sites to bar you from using a modified program with them, it is loyal to them, not to you.</p></blockquote>
<p>Principle one: the user wants to run code that will enable remote attestation. Principle two: the "computer", as a combination of hardware and software, would then be allowing remote attestation.</p>
<p>Like Odysseus and the sirens, if the design states that the users should be tied to the mast, is it disloyal to its users when they change their mind at a later, run-time, state, or should the earlier, design-time instruction for loyalty, stand? Should the computer bar code from running that would make the system, as a whole, behave in a disloyal way, or is it the right of users to tell their own systems to turn against them?</p>
<h2>Precedence of principles</h2>
<p>In other words: which of these principles is strongest? Asimov recognised this in his <a href="http://en.wikipedia.org/wiki/Three_Laws_of_Robotics">"laws" of robotics</a>. These laws are:</p>
<ol>
<li>A robot may not injure a human being or, through inaction, allow a human being to come to harm.</li>
<li>A robot must obey the orders given to it by human beings, except where such orders would conflict with the First Law.</li>
<li>A robot must protect its own existence as long as such protection does not conflict with the First or Second Law.</li>
</ol>
<p>In this setup, it is recognised that it is possible for the principles to come into contradiction with each other and an order of precedence is set. I think that the definitions for loyalty set here would also benefit from precedence. Which is stronger? "The computer will run, without prejudice, whatever software you install in it, and let that software do whatever its code says to do." or the anti-Tivoization principle of blocking remote attestation.</p>
<h2>Conclusions</h2>
<p>Much of this definition is sound but I think the remote attestation parts are weakest and need clarifying. In particular:</p>
<ol>
<li>More clearly define where this remote attestation is happening (i.e. at hardware, firmware or software levels) and what is allowed.</li>
<li>Outline whether the point of this definition is to restrict modes of operation that would allow the user to command the system to become disloyal.</li>
<li>Set an order of precedence for the principles of loyalty to avoid contradictory situations, if not resolved by #1.</li>
</ol>