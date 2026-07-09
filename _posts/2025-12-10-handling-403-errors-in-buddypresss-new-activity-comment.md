---
archive: https://wayback.archive-it.org/22123/20241101171236/https://eve.gd/2025/12/10/handling-403-errors-in-buddypressess-new_activity_comment/
date: 2025-12-10
doi: https://doi.org/10.59348/qg8yz-7974
image:
  feature: header_geek.png
layout: post
ogImage: images/header_geek.png
title: Handling 403 errors in BuddyPress's new_activity_comment
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lvov2pb2t"
---

Today I had a weird problem. Our BuddyPress activity stream comments were just not working. When you clicked the reply icon, then typed a response and pressed "post", it simply grayed out and never succeeded. I could see, in the logs, that there was a 403 Forbidden error being thrown.

I just debugged this and the answer is quite simple.

In your theme, somewhere, there should be a /buddypress/activity/entry.php file.

In there, you might have something like:

<pre><code class="language-php">wp_nonce_field( 'new_activity_comment', '_wpnonce_new_activity_comment' );</code></pre>

This is wrong. Change it to:

<pre><code class="language-php">wp_nonce_field( 'new_activity_comment', '_wpnonce_new_activity_comment_' . bp_get_activity_id() );</code></pre>

And all will be well.