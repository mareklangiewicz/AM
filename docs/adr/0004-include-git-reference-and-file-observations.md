# Include Git reference and pinned file observations in v3

On November 9, 2026, Marek explicitly requested extending v3 to cover GitHub-backed
apps that use tags or branch files instead of releases. Keep those observations
in the same normalized catalog, with genuine reference names, resolved commit
identities, separate observation times and file contents anchored to exact commits;
do not invent release/asset IDs or retain a live API fallback in recipes. This
extends ADR 0001's facts/selection boundary to non-release facts while preserving
the distinction between a release, a Git reference and a file observation.
