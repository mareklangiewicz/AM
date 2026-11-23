# Measure where the catalog's bytes go

Type: task
Label: wayfinder:task
Status: resolved
Blocked by: none

## Question

Where do the format-3 catalog's bytes go, and how much would each candidate
reduction save? Facts only; ticket 08 decides.

## Answer — November 23, 2026

Measured on the `release-catalog-v3` tree produced by run 45102289980, extracted
with `git archive`, by [scripts/02/sizes.py](../scripts/02/sizes.py) (bytes per
field, by raw YAML line) and [scripts/02/levers.py](../scripts/02/levers.py)
(derivability, asset kinds, retention), both run as
`python3 -I <script> <extracted>/repositories`.

Totals: `repositories/` 448.4 MB in 8,272 files, `provenance/` 10.9 MB. 150,791
releases, 1,486,460 assets. Releases per source: median 17, max 33 (32 plus a
stable). Largest file 0.92 MB (`chezmoi`, 3,209 assets); the 100 largest sources
are 8% of the bytes, so size is spread, not a few outliers.

Bytes by field (key, indentation and value):

| Field | MB | Share |
| --- | ---: | ---: |
| asset `digest` | 109.9 | 24.5% |
| asset `url_suffix` | 79.4 | 17.7% |
| asset `name` | 70.8 | 15.8% |
| asset `media_type` | 38.7 | 8.6% |
| asset `size` | 32.3 | 7.2% |
| asset id key lines | 28.1 | 6.3% |
| release `source_zip_url` + `source_tar_url` | 27.6 | 6.2% |
| release `download_base` | 12.8 | 2.9% |
| release `url` | 11.4 | 2.5% |
| release times (`published_at`, `created_at`, `updated_at`) | 18.0 | 4.0% |
| everything else | 19.4 | 4.3% |

Derivable from repository, tag and asset name:

- release `url` is `https://github.com/<repo>/releases/tag/<tag>` for 149,864 of 150,791 (99.4%);
- `source_zip_url`/`source_tar_url` are `https://api.github.com/repos/<repo>/{zipball,tarball}/<tag>` for 149,955 (99.4%);
- `download_base` is `https://github.com/<repo>/releases/download/<tag>/` for 138,463 of the 139,320 that have one (99.4%);
- `url_suffix` equals the asset name for 1,472,627 of 1,486,460 assets (99.1%), and its percent-encoding for another 7,050 (0.5%).

Together these URL fields are 131 MB (29%) and would shrink to about 1% if
stored only where they differ.

Other facts: 54,218 releases (36%) have a title equal to the tag; 80,621 (53%)
have `updated_at` different from `published_at`; 265,473 assets (18%) have no
digest; 481,866 (32%) omit `media_type` (octet-stream), and 329,154 carry
`zip`, the alias for `application/zip`, mostly an uploader's label, not the
file's type.

Assets by kind, from filename patterns (approximate: `levers.py`'s `kind`):

| Kind | Assets | MB |
| --- | ---: | ---: |
| checksums, signatures, metadata | 449,788 | 106.4 |
| Linux (AppImage, deb, rpm, linux/musl/gnu) | 415,895 | 102.8 |
| Windows | 234,717 | 57.0 |
| macOS | 189,966 | 47.0 |
| other, including bare tarballs | 196,094 | 46.8 |

Keeping only the N newest releases per source (share of release bytes):
N=1 6%, N=3 16%, N=8 38%, N=16 65%, N=32 100%.

Not measured: git object size after delta compression per run (the run
summary reports about 95 MB of new local objects per run), and the browser's
load time for smaller files.
