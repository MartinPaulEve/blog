# Batch categorization prompt (prompt_version: 1)

You are assigning canonical categories to a batch of posts from the blog at
`/home/martin/Programming/blog/_posts/`. You will be given a batch id and a list
of post filenames.

## Procedure

1. Read `/home/martin/Programming/blog/_categorization/taxonomy.yml` — the 24
   canonical categories with inclusion criteria. These exact strings
   (case-sensitive) are the ONLY values you may assign. Never invent, merge,
   pluralize, or re-case a category.
2. Read `/home/martin/Programming/blog/_categorization/remap.yml`.
3. For EACH post in your batch: read the ENTIRE file (front matter and full
   body). Judge from the content, not just the title. If the post's front
   matter has a legacy `categories:` list, remap each value through remap.yml
   (ignoring DROP) — the result is a HINT. Hints inform your judgment but never
   override it: if the content says otherwise, deviate and say so in `note`.
4. Assign 1–3 categories, most salient first. Every post gets at least one.
   Do not exceed three.

## Co-occurrence rules (apply these exactly; do not re-decide them)

- "Thomas Pynchon" posts do NOT also get "Literature" unless the post
  substantively discusses non-Pynchon literature too.
- "Publication: …" announcements and book launches get "Publications" plus the
  subject category of the work (e.g. a published Pynchon chapter → Publications,
  Thomas Pynchon).
- Conference papers, event reports, CFPs, workshop announcements get
  "Conferences" plus the subject category of the material.
- Year-in-review posts → "Personal" (add "Academia" only if the post is
  substantially a professional review).
- Linux fix-it posts → "Linux" alone (not also "Technology"). "Technology" is
  reserved for tech with no more specific category (hardware, Android,
  networking, platforms, tech commentary).
- Personal illness experience → "Health"; commentary on health *policy* →
  "Politics" (they may co-occur when a post does both).
- The HE Green Paper response series → "Higher Education" alone.
- Posts about OA business models/policy → "Open Access"; posts about the
  *technical tooling* of publishing (OJS, JATS, typesetting) → "Publishing
  Technology"; posts about identifiers/metadata/infrastructure → "Scholarly
  Communications". A post can hold two of these when it genuinely spans them.

## Calibration examples (gold answers — match this judgment)

| Post | Categories |
|---|---|
| 2007 "XSS Cheat Sheet" | Information Security |
| 2008 "Building a robust, SSL, CRC-Verified server/client solution in the .NET Framework" | Programming, Information Security |
| 2010 "Where to start with Thomas Pynchon?" | Thomas Pynchon |
| 2012 "A Complete List of the Ancient Greek Terms in Adorno's Aesthetic Theory" | Philosophy |
| 2012 "Starting an Open Access Journal: a step-by-step guide part 1" | Open Access, Publishing Technology |
| 2015 "HE Green Paper: response to question 1" | Higher Education |
| 2016 "I have suffered from an episode of cerebral vasculitis and a stroke" | Health, Personal |
| 2019 "I have won the 2019 Philip Leverhulme Prize" | Personal, Academia |
| 2021 "How to fix a broken Crumar Bit99 synthesizer" | Music, Technology |
| 2024 "Rusting Away (or: packing the entire Crossref database into a SQLite file)" | Programming, Scholarly Communications |
| 2026 "On (not) using AI detectors" | Artificial Intelligence, Academia |

## Output

Write EXACTLY ONE file: `/home/martin/Programming/blog/_categorization/batches/<batch-id>.yml`.
Do not write or modify anything else. Format (a LIST of records, one per post,
in the order given to you):

```yaml
prompt_version: 1
batch: <batch-id>
posts:
- file: 2011-01-04-example-post.md
  title: "Example post"
  old: [politics, HE]        # raw legacy values verbatim; [] if none
  new: [Politics, Academia]  # 1-3 canonical values, most salient first
  needs_review: false        # true when you were genuinely unsure
  note: ""                   # required non-empty when needs_review or when you overrode strong hints
```

Quote titles containing YAML-special characters. Include every post you were
given exactly once. Your final message should be only: the batch id, the count
of posts processed, and how many you flagged `needs_review`.
