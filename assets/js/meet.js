/* /meet — private Jitsi (8x8 JaaS) calls from a static page.
 *
 * Everything that matters arrives in the URL fragment, which browsers
 * never send to the server: `room` (the secret, random room name) and,
 * for the host only, `jwt` (a moderator token signed locally by
 * ./meet.sh). Without a usable room nothing from 8x8 is loaded at all.
 * With one, the JaaS loader is injected and the call fills the frame;
 * a host additionally gets a bar showing the guest link to share.
 */
(function () {
    'use strict';

    var ROOM_RE = /^[a-z0-9_-]{6,64}$/;
    var JAAS_DOMAIN = '8x8.vc';

    /* Pure: read {room, jwt, name} out of a fragment string. An invalid
       room comes back as null so callers need only one check. */
    function parseInvite(hash) {
        var params = new URLSearchParams((hash || '').replace(/^#/, ''));
        var room = (params.get('room') || '').trim().toLowerCase();
        return {
            room: ROOM_RE.test(room) ? room : null,
            jwt: params.get('jwt') || null,
            name: (params.get('name') || '').trim() || null
        };
    }

    function guestLink(room) {
        return location.origin + location.pathname + '#room=' + room;
    }

    function setStatus(title, text, link) {
        var box = document.getElementById('meet-status');
        box.innerHTML = '';
        var h = document.createElement('h1');
        h.textContent = title;
        var p = document.createElement('p');
        p.textContent = text;
        box.appendChild(h);
        box.appendChild(p);
        if (link) {
            var a = document.createElement('a');
            a.href = link.href;
            a.textContent = link.text;
            var p2 = document.createElement('p');
            p2.appendChild(a);
            box.appendChild(p2);
        }
        box.hidden = false;
    }

    function showInviteBar(room) {
        var bar = document.getElementById('meet-invite');
        var code = document.getElementById('meet-invite-link');
        var button = document.getElementById('meet-invite-copy');
        var link = guestLink(room);
        code.textContent = link;
        button.addEventListener('click', function () {
            var done = function () {
                button.textContent = 'Copied';
                setTimeout(function () { button.textContent = 'Copy'; }, 2000);
            };
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(link).then(done, function () {
                    window.prompt('Copy the guest link:', link);
                });
            } else {
                window.prompt('Copy the guest link:', link);
            }
        });
        bar.hidden = false;
    }

    function loadJaas(appId, callback) {
        if (window.JitsiMeetExternalAPI) { callback(); return; }
        var script = document.createElement('script');
        script.src = 'https://' + JAAS_DOMAIN + '/' + appId + '/external_api.js';
        script.async = true;
        script.onload = callback;
        script.onerror = function () {
            setStatus('Could not load the call',
                'The video service did not respond. Reload the page to try again.');
        };
        document.head.appendChild(script);
    }

    function startCall(appId, invite) {
        var frame = document.getElementById('jaas-container');
        var status = document.getElementById('meet-status');
        var rejoin = location.href;

        status.hidden = true;
        frame.hidden = false;

        var options = {
            roomName: appId + '/' + invite.room,
            parentNode: frame,
            configOverwrite: {
                prejoinConfig: { enabled: true },
                startWithAudioMuted: false,
                disableDeepLinking: true
            },
            interfaceConfigOverwrite: {
                SHOW_JITSI_WATERMARK: false
            }
        };
        if (invite.jwt) { options.jwt = invite.jwt; }
        if (invite.name) { options.userInfo = { displayName: invite.name }; }

        var api = new window.JitsiMeetExternalAPI(JAAS_DOMAIN, options);

        /* The moderator token is now inside the iframe; take it off the
           address bar so a screenshot or shared tab cannot leak it. The
           invite bar keeps the guest link to hand. */
        if (invite.jwt && window.history && history.replaceState) {
            history.replaceState(null, '', location.pathname + '#room=' + invite.room);
        }

        api.addEventListener('readyToClose', function () {
            api.dispose();
            frame.hidden = true;
            frame.innerHTML = '';
            document.getElementById('meet-invite').hidden = true;
            setStatus('Call ended', 'You have left the call.',
                { href: rejoin, text: 'Rejoin the call' });
        });
    }

    function init() {
        var scriptTag = document.currentScript ||
            document.querySelector('script[src*="/assets/js/meet.js"]');
        var appId = scriptTag && scriptTag.getAttribute('data-app-id');
        var invite = parseInvite(location.hash);

        if (!appId) {
            setStatus('Call room not configured',
                'The video-call tenant is not set on this site yet.');
            return;
        }
        if (!invite.room) {
            /* Leave the page's own "you need an invitation" text showing
               and, crucially, load nothing from 8x8. */
            return;
        }
        if (invite.jwt) { showInviteBar(invite.room); }
        loadJaas(appId, function () { startCall(appId, invite); });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}());
