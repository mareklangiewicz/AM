# PROTOTYPE, throwaway: see docs/design/version-catalog.md.
# Apply each recipe's convention to flattened release assets.
# Usage: awk -v arch=x86_64 -v nomatch=FILE -f pick.awk recipes.tsv assets.tsv > catalog.tsv
# assets.tsv: repo(lowercase) depth latest-depth prerelease tag published name size digest,
# sorted by repo, depth, then name bytewise (that is how REST lists assets, and
# today's `head -1` depends on it). A row with depth -1 only marks a repo as found.
# Prints "app tag published name size sha256 depth", up to KEEP rows per app.
# Repos that were found but where some recipe matched nothing go to the nomatch file.

BEGIN {
	FS = OFS = "\t"
	KEEP = 3
	if (arch == "x86_64") { other = "i386 i686 armhf aarch64 arm64 armv7l"; self = "x86_64 amd64" }
	else { other = "x86_64 amd64 armv7l i386 i686 armhf"; self = "aarch64 arm64" }
	nother = split(other, OTHER, " ")
	nself = split(self, SELF, " ")
}

FNR == NR {
	n++
	app[n] = $1; repo[n] = $2; conv[n] = $3
	k = tolower($2)
	ids[k] = ids[k] " " n
	next
}

{ found[$1] = 1 }
$2 < 0 { next }
{
	m = split(ids[$1], list, " ")
	for (j = 1; j <= m; j++) try(list[j])
}

function arch_ok(name, policy,    i) {
	name = tolower(name)
	for (i = 1; i <= nother; i++) if (index(name, OTHER[i])) return 0
	if (policy == "excl") return 1
	for (i = 1; i <= nself; i++) if (index(name, SELF[i])) return 1
	return 0
}

function try(i,    c, d, L) {
	if (cnt[i] == KEEP || (i, $2) in got) return
	split(conv[i], c, ":")
	d = $2 + 0; L = $3 + 0
	if (c[1] == "latest" && (L < 0 || d < L || (d > L && $4 == "true"))) return
	if (tolower($7) !~ /\.appimage$/ || !arch_ok($7, c[3])) return
	got[i, $2] = 1
	cnt[i]++
	print app[i], $5, $6, $7, $8, $9, $2
}

END {
	for (i = 1; i <= n; i++) {
		k = tolower(repo[i])
		if (!(k in found)) missing++
		else if (!cnt[i]) { nomatched++; if (!(k in sent)) { sent[k] = 1; print repo[i] > nomatch } }
	}
	printf "apps %d, repo missing %d, no match %d\n", n, missing, nomatched > "/dev/stderr"
}
