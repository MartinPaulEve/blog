# dotPublic compliance — remaining work

This is a private working note (untracked, not committed). It records what the
dotPublic scan of <https://eve.gd> still flags **after** the changes now on
`main`, why I could not finish each item myself, and how you can close it.

## First, the important caveat

The scanner reads the **live** site. Everything I changed is committed to `main`
but **not deployed** — so a re-scan today will still show the old score. Deploy,
then re-scan at <https://dotpublic.org/checker/scan> to see the real result.

Also worth knowing: the scanner runs its automated accessibility checks in
**light mode** only. That matters for the dark-mode note at the bottom.

## What has already been fixed (for your reference)

Starting point was **37/74**. The changes on `main` should turn the following
from FAIL/SKIP to PASS once deployed (≈30 checks): the `link-name` a11y
violation, skip-navigation link, footer-credit colour contrast, self-hosted
fonts + highlight.js (removes the Google Fonts data-leak), `robots.txt` with AI
crawler rules, `security.txt`, and the six new pages (`/accessibility/`,
`/privacy/`, `/ai/`, `/contact/`, `/security/`, `/colophon/`) which between them
cover the accessibility statement, privacy/data-practices/retention checks,
AI-use and oversight checks, contact/response/complaints/appeals checks,
incident-response and responsible-disclosure checks, continuity, open-source and
algorithmic-transparency checks. Estimated new score: **mid-to-high 60s / 74**.

I verified the accessibility fixes with axe-core locally: in light mode the
homepage and all six new pages report **zero** violations.

The items below are what I could **not** fully resolve.

---

## Still failing — needs something only you can supply

### `inter-002` — Published uptime/status page
**Why not done:** a genuine status page has to be backed by a real uptime
monitor; a hand-written "all systems operational" HTML page would be dishonest
and probably won't satisfy the check.
**How to fix:** set up a free monitor (UptimeRobot, BetterStack/Better Uptime,
or Instatus all have free public status pages), point it at eve.gd, then link
its public page from the footer (and optionally add a `/status/` redirect to it).
Ten minutes once you pick a provider.

### `resp-001` — Environmental / sustainability disclosure
**Status:** partially addressed on `/colophon/` (static site, minimal JS,
self-hosted fonts, small pages). It will likely still fail two sub-criteria:
- *specific_metrics* — needs a real number (e.g. grams CO₂ per page view).
- *hosting_disclosure* — needs the hosting provider named and its energy mix.

**Why not done:** I don't know who hosts eve.gd or whether they run on renewable
energy, and I can't produce audited carbon figures.
**How to fix:** run the page through the Website Carbon Calculator
(<https://www.websitecarbon.com/>) or add the `co2.js` badge, paste the gCO₂
figure into the colophon's sustainability section, name your host, and state
whether it uses renewable energy (many hosts publish this; check the Green Web
Foundation directory at <https://www.thegreenwebfoundation.org/green-web-check/>).

### `trans-006` — Funding disclosed with detail
**Status:** partially addressed — `/colophon/` names COPIM's funders (Research
England, Arcadia) and the Leverhulme Trust prize. The check also wants
*grant amounts / reference numbers* and *complete* coverage of your funded work.
**Why not done:** I don't have your grant reference numbers, amounts, or the full
list of funded projects.
**How to fix:** add a short funding table to the colophon with each project, its
funder, and the grant reference/amount where you're willing to disclose it.

### `resp-003` — Worker wellbeing policy
**Why not done:** this is genuinely not applicable to a one-person personal site,
and I won't invent a policy about pay/hours/benefits for staff who don't exist —
the rubric explicitly wants concrete commitments on those, which an honest "I
have no employees" statement won't satisfy.
**How to fix (optional):** either accept this as a permanent N/A, or, if you ever
engage collaborators/RAs, publish the working-conditions commitments you offer
them. Not worth chasing for a personal site.

### `acct-005` — Published moderation policies
**Why not done:** not applicable — the site hosts no user-generated content or
comments, so there is nothing to moderate. The rubric wants a real moderation
policy with criteria and enforcement.
**How to fix (optional):** if you ever enable comments, add a `/moderation/` page.
Otherwise a one-line "this site carries no user-generated content, so no
moderation policy applies" on the colophon may or may not satisfy the AI grader —
low value, safe to leave.

---

## Uncertain — my content may pass, but flag for a re-check after deploy

### `trans-007` — Governance structure disclosed
`/colophon/` states plainly that this is a personal site with sole editorial
responsibility and no governing body. That's the honest answer, but the rubric
leans toward "roles within a governing/editorial body," so it may still fail.
If it does, it's a true N/A — there is no committee to describe.

### `trans-001b` — Contact form present
`/contact/` provides a prominent mailto link with a pre-filled subject as a
"form" alternative, because a static site has no server to receive a form post.
If the checker insists on a real submittable `<form>`, the only options are a
third-party form backend (Formspree, Web3Forms, etc.) — which reintroduces a
third-party request and slightly undercuts the privacy checks you just passed.
My recommendation: leave the mailto approach unless the check specifically
demands a form; the trade-off isn't worth it.

### `trans-001a` — Contact email present
Now addressed via `/contact/` (visible plain-text email + mailto). One nuance:
in the original scan this failed even though a `mailto:` was already in the nav
and footer, which suggests the checker inspects **main page body content**, not
the header/footer chrome. The new `/contact/` page puts the address in the body,
so it should pass — but if it doesn't, consider adding a visible contact line to
the homepage body (`index.md`) as well.

---

## Bonus finding (not scored by dotPublic, but a real accessibility bug)

While running axe-core I found that in **dark mode** two elements fall just below
WCAG AA contrast — site-wide, and pre-existing (they affect `/about/` and every
post, not just the new pages):

- The nav **Contact** button: white text on `#e63946` = **4.16:1** (needs 4.5).
- In-content **links** in the post body: `#e63946` on `#161616` = **4.34:1**.

The scanner didn't catch these because it tests light mode, where the same
elements use the darker `#b3122a` red and pass comfortably.

**Why I didn't change it:** the fix is to lighten the dark-mode accent red, and
that red is your core brand colour — a design decision I didn't want to make
unilaterally. It's a small nudge if you want it: in `assets/css/styles.css`, in
the `[data-theme="dark"]` block, raising the link/button red from `#e63946` to
roughly `#ff5d67` (or brighter) clears 4.5:1 on the dark background. Test it
against the "striking red" look you want before committing.
