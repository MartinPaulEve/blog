---
layout: meet
title: Meet
excerpt: "Martin Paul Eve's private video-call room. Joining needs an invitation link."
pdf: false
og_card: false
comments: false
---

<div id="meet-status" class="meet-status" role="status" aria-live="polite">
    <h1>Meet</h1>
    <p>This is my video-call room. Joining needs an invitation link from me: the one you were sent opens the call automatically, so if you are seeing this, check you followed the whole link.</p>
</div>

<div id="meet-invite" class="meet-invite" hidden>
    <span class="meet-invite-label">Guest link to share:</span>
    <code id="meet-invite-link" class="meet-invite-link"></code>
    <button type="button" id="meet-invite-copy" class="btn btn-secondary meet-invite-copy">Copy</button>
</div>

<div id="jaas-container" class="meet-frame" hidden></div>

<script src="/assets/js/meet.js?v={{ '/assets/js/meet.js' | asset_version }}" defer
        data-app-id="{{ site.data.meet.app_id }}"></script>
