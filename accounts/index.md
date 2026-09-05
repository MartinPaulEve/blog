---
layout: page
title: Accounts
tags: [accounts, contact, identity]
comments: false
---

<link href="/assets/css/accounts.css?v={{ site.time | date: '%s' }}" rel="stylesheet" type="text/css">

This page is the canonical list of my accounts and public keys around the web. If you come across an account claiming to be me that is not listed here or on my [contact page](/contact/), it probably isn't me. This site also publishes a machine-readable declaration of human authorship at [/human.json](/human.json).

<div class="accounts-grid">

<section class="account-box">
<h2 class="account-box-title">Social</h2>
<ul>
<li><span class="account-service">Bluesky</span> <a class="account-handle" href="https://bsky.app/profile/eve.gd">@eve.gd</a></li>
<li><span class="account-service">Mastodon</span> <a class="account-handle" href="https://hcommons.social/@mpe">@mpe@hcommons.social</a></li>
<li><span class="account-service">LinkedIn</span> <a class="account-handle" href="https://uk.linkedin.com/in/martin-eve-382303378">Martin Eve</a></li>
</ul>
</section>

<section class="account-box">
<h2 class="account-box-title">Code</h2>
<ul>
<li><span class="account-service">GitHub</span> <a class="account-handle" href="https://github.com/MartinPaulEve">MartinPaulEve</a></li>
<li><span class="account-service">GitLab</span> <a class="account-handle" href="https://gitlab.com/MartinPaulEve">MartinPaulEve</a></li>
</ul>
</section>

<section class="account-box">
<h2 class="account-box-title">Scholarship</h2>
<ul>
<li><span class="account-service">Knowledge Commons</span> <a class="account-handle" href="https://hcommons.org/members/martin_eve/">martin_eve</a></li>
<li><span class="account-service">KC Works</span> <a class="account-handle" href="https://works.hcommons.org/search?q=metadata.creators.person_or_org.name%3A%22Eve%2C%20Martin%20Paul%22">my works</a></li>
<li><span class="account-service">BIROn</span> <a class="account-handle" href="https://eprints.bbk.ac.uk/view/people/Eve=3AMartin_Paul=3A=3A.html">my deposits</a>
<span class="account-note">Birkbeck's institutional repository.</span></li>
</ul>
</section>

<section class="account-box">
<h2 class="account-box-title">Music</h2>
<ul>
<li><span class="account-service">Bandcamp</span> <a class="account-handle" href="https://coursecorrection.bandcamp.com">Course Correction</a>
<span class="account-note">My band; solo releases as Martin Eve are on the <a href="/music/">music page</a>.</span></li>
<li><span class="account-service">tici taci</span> <a class="account-handle" href="https://ticitaci.com">ticitaci.com</a>
<span class="account-note">The label my solo releases appear on.</span></li>
</ul>
</section>

<section class="account-box">
<h2 class="account-box-title">Email</h2>
<ul>
<li><span class="account-service">Personal (preferred)</span> <a class="account-handle" href="mailto:martin@eve.gd">martin@eve.gd</a></li>
<li><span class="account-service">Birkbeck</span> <a class="account-handle" href="mailto:martin.eve@bbk.ac.uk">martin.eve@bbk.ac.uk</a></li>
<li><span class="account-service">Michigan State</span> <a class="account-handle" href="mailto:eve@msu.edu">eve@msu.edu</a></li>
</ul>
</section>

<section class="account-box">
<h2 class="account-box-title">This site</h2>
<ul>
<li><span class="account-service">Posts</span> <span class="account-handle">{{ site.posts | size }}{% assign oldest_post = site.posts | last %}, since {{ oldest_post.date | date: "%Y" }}</span></li>
<li><span class="account-service">Categories</span> <span class="account-handle">{{ site.categories | size }}</span></li>
<li><span class="account-service">Tags</span> <span class="account-handle">{{ site.tags | size }}</span></li>
<li><span class="account-service">Page generated</span> <span class="account-handle">{{ site.time | date: "%-d %B %Y" }}</span></li>
<li><span class="account-service">human.json</span> <a class="account-handle" href="/human.json">/human.json</a>
<span class="account-note">Human-authorship declaration and vouches; see also the <a href="/ai/">AI use policy</a>.</span></li>
</ul>
</section>

<section class="account-box account-box--wide">
<h2 class="account-box-title">Projects &amp; sites</h2>
<ul>
<li><span class="account-service">Open Library of Humanities</span> <a class="account-handle" href="https://openlibhums.org">openlibhums.org</a>
<span class="account-note">I founded the OLH and was its CEO for ten years.</span></li>
<li><span class="account-service">Janeway</span> <a class="account-handle" href="https://janeway.systems">janeway.systems</a>
<span class="account-note">Co-founder of this journal-publishing platform; I wrote the original codebase with Andy Byers.</span></li>
<li><span class="account-service">Open Book Collective</span> <a class="account-handle" href="https://openbookcollective.org">openbookcollective.org</a>
<span class="account-note">I built this website, as part of DQ Programming LLP.</span></li>
<li><span class="account-service">Open Journals Collective</span> <a class="account-handle" href="https://openjournalscollective.org">openjournalscollective.org</a>
<span class="account-note">I built this website, as part of DQ Programming LLP.</span></li>
<li><span class="account-service">Fluke FM</span> <a class="account-handle" href="https://fluke.fm">fluke.fm</a>
<span class="account-note">I built and run this site.</span></li>
</ul>
</section>

<section class="account-box account-box--wide">
<h2 class="account-box-title">Public keys</h2>

<p>These are my current public keys for <strong>martin@eve.gd</strong>. Anything signed with other keys, or keys bearing other identities, should not be assumed to be mine.</p>

<p><strong>SSH</strong> (Ed25519; also used to sign my git commits):</p>
<pre class="account-key">ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKKjbi7dBrGRlTGDhWb5cPshqCdNkIos+Z5wwM6ijIXN martin@eve.gd</pre>

<p><strong>PGP</strong> (RSA-4096, created February 2025; also on <a href="https://keys.openpgp.org/vks/v1/by-email/martin@eve.gd">keys.openpgp.org</a>). Fingerprint:</p>
<p class="account-fingerprint">01CB C586 BF61 49E8 96BF  B360 70A0 BE94 A3D4 B37E</p>

<details>
<summary>Show the full PGP public key</summary>
<pre class="account-key">-----BEGIN PGP PUBLIC KEY BLOCK-----
Comment: 01CB C586 BF61 49E8 96BF  B360 70A0 BE94 A3D4 B37E
Comment: Martin Paul Eve &lt;martin@eve.gd&gt;

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
=sMyu
-----END PGP PUBLIC KEY BLOCK-----</pre>
</details>
</section>

</div>
