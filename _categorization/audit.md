# Category assignment audit

Audit of `review.md` against the criteria in `taxonomy.yml`, judging by titles only.
Items already self-flagged by the batch agents in the "Needs review" section are not
re-reported here. Suggested category sets are indicative, not prescriptive.

## 1. Posts likely in a wrong category

- 2020-08-18-rethinking-assessment-during-the-pandemic.md — currently [Open Access, Teaching] — suggest [Teaching, Higher Education, Health] — "Rethinking assessment during the pandemic, particularly re. disability equality" has no open-access signal at all; its presence in the OA list looks like batch line-drift.
- 2011-06-01-william-gibson-cory-doctorow-diane-coyle-and-mark-stevenson-at-the-british-library.md — currently [Literature, Philosophy] — suggest [Conferences, Literature] — an attended-event report exactly like "Russell Hoban in Conversation with Will Self at the British Library" (Conferences + Literature); none of the four speakers is a philosopher, so Philosophy is hard to justify.
- 2026-01-15-wordpress-loading-theme-assets-of-a-different-theme-to-that-selected.md — currently [Technology] — suggest [Programming] — every comparable WordPress debugging/fix post (full-site-editor hacking, BuddyPress 403s, wp-aspxrewriter) is in Programming; Technology is defined as fallback-only when no more specific category fits.
- 2016-02-26-the-critique-of-utopia.md — currently [Literature, Scholarly Communications] — suggest [Philosophy, Scholarly Communications] — a critique of utopia(nism) is critical theory, squarely within Philosophy's criteria; nothing in the title suggests literary criticism.
- 2016-02-26-rethinking.md ("A world reimagined without the university") — currently [Conferences, Scholarly Communications] — suggest [Scholarly Communications, Higher Education] — no paper/talk/CFP/event signal in the title; Conferences membership looks like drift (same-day sibling of the previous item, both apparently thought-experiment posts).
- 2019-06-01-what-size-should-my-music-studio-be.md — currently [Music, Programming] — suggest [Music] — a studio-design question with no code signal in the title; Programming looks misfiled unless the post is actually about a room-calculation script (worth a content check).
- 2013-09-18-publication-gatekeepers-in-a-digital-wasteland-the-author.md — currently [Literature, Publications] — suggest [Publications, Academia] — "Gatekeepers in a digital wasteland" (in The Author) is by its title a piece about publishing gatekeeping, not literary criticism; Literature looks like the wrong subject pairing.

## 2. Inconsistent treatment of series / sibling posts

Series verified as fully consistent (no action needed): HE Green Paper responses q1–28 plus the summary post (all Higher Education); the Adorno terminology / Greek lexicon series (all Philosophy); "Starting an Open Access Journal" parts 1–5 + table of contents (all Open Access + Publishing Technology); year-in-review posts 2011–2025 (all Academia + Personal); every "Publication: ..." post is in Publications; every "Conference Paper: ..." post is in Conferences; Pynchon in Public Day, Picture This, First Fictions, SA4QE, OJS-plugin, meTypeset, .NETIDS, and Zotero-on-Ubuntu series are internally consistent.

Deviating members found:

- 2010-03-19-international-pynchon-week-2010-abstracts.md — currently [Conferences, Literature, Thomas Pynchon] — suggest [Conferences, Thomas Pynchon] — all other IPW posts (Day 1/2/3, 2013 CFP, "On International Pynchon Week") are Conferences + Thomas Pynchon; Literature's criteria explicitly exclude Pynchon.
- 2011-02-21-mendeley-for-android-update.md — currently [Programming] — suggest [Programming, Technology] (or drop Technology from the whole series, see section 3) — the other seven Mendeley-for-Android posts are all Programming + Technology; this is the lone deviant.
- 2012-10-19-orbit-1-2-is-now-open-and-our-rolling-format-is-live.md — currently [Thomas Pynchon] — suggest [Open Access, Thomas Pynchon] — every other Orbit operational announcement (launch, 1.1 update, LMU funding, going live) pairs Open Access with Thomas Pynchon; the "rolling format / open" announcement is exactly that kind of journal-operations news.
- 2022-01-09-authorship.md — currently [Literature, Philosophy] — suggest [Literature] — the only member of the 2022 novel-survey series (Adaptation, Bildungsroman, The Arabic Novel, etc.) that carries a second category; all its siblings are Literature only.
- 2022-10-10-the-politics-of-peer-review-and-preprints-in-the-real-world.md — currently [Academia, Health, Politics] — suggest aligning with its near-twin 2022-10-12-the-uks-department-for-health-and-preprints.md [Academia, Politics] — two posts on the same preprints topic two days apart; Health should be on both or neither.
- 2012-05-05-excursions-journal-vol-3-launch-party.md — currently [Academia] — suggest aligning with 2011-06-21-excursions-vol-2-issue-1-virus-2011.md [Academia, Publications] — sibling issue announcements for the same journal handled differently (and a launch party is arguably Conferences); note the vol. 2 post's Publications membership is itself already queried in "Needs review", so resolve the pair together.
- 2011-04-16-david-foster-wallaces-the-pale-king-bonnie-nadell-and-michael-pietsch-at-foyles.md — currently [Literature] — suggest [Conferences, Literature] — an attended literary-event report; the equivalent Hoban/Will Self event got Conferences + Literature (see also the Gibson/Doctorow finding in section 1).
- 2013-11-15-some-diagrams-of-jennifer-egan-novels.md — currently [Academia, Literature] — suggest [Literature, Digital Humanities] — the closely comparable visualization posts (Visualizing Gravity's Rainbow, SankeyVariant, the early-GR-visualizations retrospective) all sit in Digital Humanities.
- 2010-03-11-sshsplit-featured.md — currently [Programming] — suggest [Programming, Information Security] — the sshsplit announcement itself is Information Security + Programming; the follow-up "featured" note dropped InfoSec.
- 2016-06-19-cassius-now-supports-full-headless-pdf-creation-from-jats.md — currently [Programming, Publishing Technology] — suggest [Publishing Technology] — the two other CaSSius posts (announcement, getting started) are Publishing Technology only; minor drift either way, but the trio should match.
- 2011-01-19-rockaby-mission-statement-and-implementation-plans.md — currently [Digital Humanities, Programming] — suggest [Programming] — the other two Rockaby posts are Programming only; DH may be content-justified for a mission statement, but the series is split.

## 3. Category-level over-/under-inclusiveness

### Technology (fallback-only rule)

Technology's criteria say to use it "only when no more specific technical category fits", yet several early posts double it onto a more specific home:

- Mendeley-for-Android series (2010-12-20 through 2011-01-24, 7 posts) — currently [Programming, Technology] — suggest [Programming] — app-development posts already fully covered by Programming; the doubling appears to be batch habit rather than criteria-driven.
- 2011-01-09-android-rom-update-utility-extractor-for-linux.md — currently [Linux, Programming, Technology] — suggest [Linux, Programming] — three technical categories on one post; Technology is redundant given two more specific homes.
- 2011-01-08-automated-cpanel-backups-with-scp.md — currently [Programming, Technology] — suggest [Programming] — a scripting how-to, no fallback needed.
- 2011-04-21-crossword-helper-for-android.md — currently [Programming, Technology] — suggest [Programming] — its sibling "Online crossword helper" is Programming only.
- 2010-08-15-htc-wildfire-stage-1-soft-root.md — currently [Information Security, Technology] — suggest [Information Security] — rooting is a penetration technique already housed in InfoSec; weaker call since Technology names Android/hardware explicitly.

The remaining Technology-only entries (networking kit, mesh conversion, gadget resets, hardware notes, broad tech commentary) fit the criteria well; no under-inclusion found.

### Conferences

- 2010-03-15-humanities-map.md — currently [Academia, Conferences] — suggest [Academia] — no paper/report/CFP/workshop signal in the title.
- 2011-05-27-academic-businesss-cards.md — currently [Academia, Conferences] — suggest [Academia] — networking advice, not an event, paper, or CFP.

Otherwise the 91 Conferences entries are overwhelmingly genuine papers, event reports, CFPs, and workshops.

### Publications

Criteria limit this category to announcements of the author's own published work; press coverage has been handled inconsistently across batches:

- 2011-05-16-photograph-and-interview-in-the-guardian.md — currently [Publications, Thomas Pynchon] — suggest [Personal, Thomas Pynchon] — press coverage of the author, not his published work.
- 2012-04-05-new-york-times-writes-about-my-ph-d-thesis-work.md — currently [Philosophy, Publications, Thomas Pynchon] — suggest [Thomas Pynchon, Personal] — press coverage; contrast the Library Journal Q&A (2013-01-16) and ProfHacker interview (2014-04-22), which other batches correctly kept out of Publications.
- 2015-01-18-stephen-curry-stephen_curry-reviews-open-access-and-the-humanities.md — currently [Open Access, Publications] — suggest [Open Access] — a review of his book by someone else (reception news, not his output); borderline, since the category does host book-related news.

All "Publication: ..." titled posts are correctly present; no under-inclusion found.

### Thomas Pynchon vs Literature

Beyond the IPW 2010 Abstracts post (section 2), no unwarranted doubling found: every other Literature/Pynchon overlap involves a genuinely dual-subject piece (Pynchon with David Foster Wallace, DeLillo, or American-postmodernism surveys), which the Literature criteria accommodate. None found otherwise.

### Health

- 2026-04-17-thinking-about-dogs.md — currently [Health, Personal] — suggest [Personal] — the taxonomy uses this exact title as the Personal exemplar ("family, dogs"); Health is dubious unless the post ties dog ownership to illness/disability, which the title does not signal.

The remainder of Health is well-scoped: illness-from-lived-experience posts, with COVID-policy items sensibly doubled into Politics.

## Overall assessment

Assignment quality is high. The headline series that were most at risk of batch drift — the 28-part HE Green Paper responses, the Adorno terminology run, the Starting an Open Access Journal guide, fifteen years of year-in-review posts, and the full "Publication:" and "Conference Paper:" corpora — are all perfectly consistent across what were independent batch agents, and the "Needs review" section shows the agents self-flagged genuinely hard cases with sound reasoning. The residual problems are few and mostly low-stakes: one clear cross-domain misfile (the pandemic-assessment post under Open Access), a handful of single-member series deviations (IPW abstracts, Orbit 1.2, the novel-survey "Authorship" post, one Mendeley post), a systematic but confined tendency in the 2010–11 batches to double Programming posts into Technology against that category's fallback-only rule, and inconsistent handling of press coverage in Publications. Fixing the roughly two dozen items listed above would bring the corpus to a very clean state; no category needs wholesale reassignment.
