---
archive: https://wayback.archive-it.org/22123/20231101171300/https://eve.gd/2025/04/17/hacking-the-full-site-editor-in-wordpress
date: 2025-04-17
doi: https://doi.org/10.59348/14x3a-hw13
roguescholar: https://rogue-scholar.org/records/q06px-sw175
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lvtlk2w2r
image:
  feature: header_kcw.png
layout: post
ogImage: images/header_kcw.png
title: Hacking the full site editor in WordPress
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7lvtlk2w2r"
categories:
- Programming
kcworks: https://works.hcommons.org/records/ng3z2-0rr85
references:
- title: Knowledge Commons
  type: WebSite
  url: https://hcommons.org
- https://hcommons.org/app/plugins/hc-styles/css/fix-for-highlight-bug.css # KC highlight bug fix CSS file
---

Today, I have been battling a frustrating bug. In the latest versions of Chrome and Edge, users cannot highlight text in Full Site Editor or Post/Page Editor in WordPress (at [Knowledge Commons](https://hcommons.org). This turned out to be a complete nightmare to fix.

What was actually happening was that highlights were transparent, due to this block of CSS in load-styles.php:

	.block-editor-block-list__layout::selection {
	    background: transparent;
	}

The way to fix it is to apply this (which gives a hard-coded green and white highlight):

	.block-editor-block-list__layout::selection {
	    background: green !important;
	    color: white !important;
	}


The problem is, this selector has to be applied AFTER Full Site Editor loads and populates its iframe. The iframe does NOT run through standard WordPress hooks. It won't let you add an action to "wp_footer" for instance. So there was no easy way to get a stylesheet into the iframe, at the end, using standard WordPress hooks and actions.

What I eventually did was very hacky. First, I had to load our javascript from a plugin, using:

	wp_enqueue_script("hc-append", plugins_url( '/hc-styles/js/append.js' ));

Then in js/append.js, I have:


	(function () {
	    console.log("Injecting CSS");
	    const cssHref = 'https://hcommons.org/app/plugins/hc-styles/css/fix-for-highlight-bug.css';
	    const selector = 'iframe[name="editor-canvas"]';
	    function injectStylesheet(iframe) {
	        try {
	            const doc = iframe.contentDocument || iframe.contentWindow.document;
	            const link = doc.createElement('link');
	            link.rel = 'stylesheet';
	            link.href = cssHref;
	            link.type = 'text/css';
	            link.media = 'all';
	            doc.body.appendChild(link);
	            console.log(doc);
	        } catch (e) {
	            console.error('Failed to inject CSS into iframe:', e);
	        }
	    }
	    function waitForIframeAndInject() {
	        const iframe = document.querySelector(selector);
	        if (iframe && iframe.contentDocument && iframe.contentDocument.readyState === 'complete') {
	            classes = iframe.contentDocument.body.classList;
	            for (cls of classes) {
	                console.log("Testing for: " + cls);
	                if (cls == "block-editor-iframe__body") {
	                    console.log("Found block-editor-iframe__body. Injecting.");
	                    setTimeout(injectStylesheet(iframe), 500);
	                    return
	                }
	            }
	            console.log("Waiting...");
	            setTimeout(waitForIframeAndInject, 1000); // try again shortly
	        } else {
	            console.log("Waiting...");
	            setTimeout(waitForIframeAndInject, 1000); // try again shortly
	        }
	    }
	    window.addEventListener('load', waitForIframeAndInject);
	})();

So what we do is loop, waiting for the iframe to appear and for its body to gain the class attribute "block-editor-iframe__body". We check every second for this. When it appears, we inject the stylesheet INTO the iframe's body, as the last element. This ensures it is loaded AFTER all of the others and that our ::selected pseudo-element selector does the job.

I hope that this is fixed in future versions of Full Site Editor and/or Chrome, but for now, this somewhat untidy and unsatisfying solution will have to do.