# PROTOTYPE, throwaway: see docs/design/version-catalog.md.
# Classify AM scripts into recipe rows by their first version= line.
# Usage: awk -v arch=x86_64 -f classify.awk programs/x86_64/* > recipes.tsv
# Prints "app<TAB>repo<TAB>order:appimage:policy" rows, and skip reasons on stderr.

BEGIN {
	SED = "sed 's/[()\",{} ]/\\n/g'"
	kind["grep -oi \"https.*mage$\""] = "url"
	kind["grep -oi \"https.*download.*mage$\""] = "url"
	kind["grep -oi \"https.*download.*\""] = "anyurl"
	kind["grep -i \"appimage$\""] = "filter"
	split("i386 i686 armhf aarch64 arm64 armv7l x86_64 amd64 x64 x86", w, " ")
	for (i in w) ARCH[w[i]] = 1
	if (arch == "x86_64") split("x86_64 amd64 x64 x86", w, " ")
	else split("aarch64 arm64", w, " ")
	for (i in w) SELF[w[i]] = 1
}

FNR == 1 { flush(); file = FILENAME; first = ""; differ = 0 }

{
	line = $0
	sub(/^[ \t]+/, "", line)
	sub(/[ \t\r]+$/, "", line)
	if (substr(line, 1, 8) != "version=") next
	if (first == "") first = line
	else if (line != first) differ = 1 # installer and AM-updater disagree
}

END {
	flush()
	for (r in why) printf "%6d skip: %s\n", why[r], r | "sort -rn >&2"
	for (r in conv) printf "%6d %s\n", conv[r], r | "sort -rn >&2"
}

function flush(    app, r) {
	if (file == "") return
	if (first == "") { why["no version= line"]++; return }
	if (index(first, "api.github.com") == 0) { why["not github"]++; return }
	if (differ) { why["version= lines differ"]++; return }
	r = classify(first)
	if (r ~ /\t/) {
		app = file
		sub(/.*\//, "", app)
		print app "\t" r
		sub(/.*\t/, "", r)
		conv[r]++
	} else why[r]++
}

# Words of a grep pattern like "i386\|i686", lowercased, into the array out.
function words(pat, out,    i) {
	while ((i = index(pat, "\\|")) > 0) pat = substr(pat, 1, i - 1) " " substr(pat, i + 2)
	return split(tolower(pat), out, " ")
}

# Pattern inside `<prefix>"..."`, or "" when s has another shape.
function quoted(s, prefix,    p) {
	if (substr(s, 1, length(prefix)) != prefix || substr(s, length(s)) != "\"") return ""
	p = substr(s, length(prefix) + 1, length(s) - length(prefix) - 1)
	return index(p, "\"") ? "" : p
}

# Returns "repo<TAB>convention" or a skip reason (no tab).
function classify(line,    n, st, i, s, p, parts, latest, nurl, nany, nfilt, narch, policy, m, w, j, ok) {
	n = split(line, st, / \| /) # never bare "|": the patterns contain \|
	for (i = 1; i <= n; i++) { sub(/^ +/, "", st[i]); sub(/ +$/, "", st[i]) }
	s = st[1]
	p = "version=$(curl -Ls "
	if (substr(s, 1, length(p)) != p) return "endpoint:other"
	s = substr(s, length(p) + 1)
	sub(/^'/, "", s)
	sub(/'$/, "", s)
	p = "https://api.github.com/repos/"
	if (substr(s, 1, length(p)) != p) return "endpoint:other"
	m = split(substr(s, length(p) + 1), parts, "/")
	if (parts[1] == "" || parts[2] == "" || parts[1] parts[2] ~ /['" \t]/ || parts[3] != "releases") return "endpoint:other"
	if (m == 3) latest = 0
	else if (m == 4 && parts[4] == "latest") latest = 1
	else return "endpoint:other"
	if (n < 3 || st[2] != SED || st[n] != "head -1)") return "shape:other"
	policy = "excl"
	for (i = 3; i < n; i++) {
		s = st[i]
		if (s in kind) {
			if (kind[s] == "url") nurl++
			else if (kind[s] == "anyurl") nany++
			else nfilt++
			continue
		}
		ok = 0
		if ((p = quoted(s, "grep -vi \"")) != "") {
			m = words(p, w); ok = 1
			for (j = 1; j <= m; j++) if (!(w[j] in ARCH) || w[j] in SELF) ok = 0
		} else if ((p = quoted(s, "grep -i \"")) != "") {
			m = words(p, w); ok = 1; policy = "incl"
			for (j = 1; j <= m; j++) if (!(w[j] in SELF)) ok = 0
		}
		if (!ok) return "pattern"
		narch++
	}
	if (narch == 1 && (nurl == 1 && nany + nfilt == 0 || nany == 1 && nfilt == 1 && nurl == 0))
		return parts[1] "/" parts[2] "\t" (latest ? "latest" : "newest") ":appimage:" policy
	if (narch == 1 && nany == 1 && nurl + nfilt == 0) return "any asset (no convention)"
	return "stages:other"
}
