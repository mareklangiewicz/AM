# shellcheck shell=sh
# vc.sh - composable POSIX sh functions for the AM version catalog.
# TSV columns (header line starts with '#'):
#   name repo tag date size url status
# status: ok | unknown | archived | error. Empty fields are '-'.

VC_HEADER='#name	repo	tag	date	size	url	status'

# vc_version_line FILE -> first version= line of an AM script
vc_version_line() { grep -m1 '^version=' "$1" 2>/dev/null; }

# vc_repo_of LINE -> owner/repo if line uses api.github.com/repos/O/R/releases[/latest]
vc_repo_of() {
  printf '%s\n' "$1" | sed -n 's|.*api\.github\.com/repos/\([A-Za-z0-9._-]*\)/\([A-Za-z0-9._-]*\)/releases.*|\1/\2|p' | head -n 1
}

# vc_endpoint_of LINE -> latest | list | (empty)
vc_endpoint_of() {
  case $1 in
    *api.github.com/repos/*/releases/latest*) echo latest ;;
    *api.github.com/repos/*/releases*) echo list ;;
  esac
}

# vc_classify DIR < names -> "name<TAB>repo" (repo '-' when unsupported)
vc_classify() {
  while IFS= read -r n; do
    [ -n "$n" ] || continue
    r=$(vc_repo_of "$(vc_version_line "$1/$n")")
    printf '%s\t%s\n' "$n" "${r:--}"
  done
}

# vc_names < x86_64-apps -> app names (lines look like "◆ name : desc")
vc_names() { awk '{ n = ($1 == "◆") ? $2 : $1; if (n != "" && n !~ /^#/) print n }'; }

# vc_repos < classified -> unique repos
vc_repos() { cut -f2 | grep -v '^-$' | sort -u; }

# vc_fetch REPO CACHEDIR -> path of cached JSON for /releases/latest.
# Conditional request with ETag; honours GITHUB_TOKEN. Curl is $VC_CURL.
vc_fetch() {
  k=$(printf '%s' "$1" | tr '/' '_'); d=$2; mkdir -p "$d"
  set -- "$1" "$d/$k.json" "$d/$k.etag" "$d/$k.hdr"
  et=; [ -s "$3" ] && [ -s "$2" ] && et=$(cat "$3")
  code=$(${VC_CURL:-curl} -sS -L -o "$2.new" -D "$4" -w '%{http_code}' \
    -H 'Accept: application/vnd.github+json' \
    ${GITHUB_TOKEN:+-H "Authorization: Bearer $GITHUB_TOKEN"} \
    ${et:+-H "If-None-Match: $et"} \
    "${VC_API:-https://api.github.com}/repos/$1/releases/latest") || code=000
  case $code in
    200) mv "$2.new" "$2"
         sed -n 's/^[Ee][Tt][Aa][Gg]: *\(.*\)\r*$/\1/p' "$4" | tr -d '\r' > "$3" ;;
    304) rm -f "$2.new" ;;
    *) rm -f "$2.new"; echo "$code" > "$2.err"; return 1 ;;
  esac
  rm -f "$2.err"; printf '%s\n' "$2"
}

# vc_rate_ok HDRFILE -> fails when x-ratelimit-remaining is 0
vc_rate_ok() {
  r=$(sed -n 's/^[Xx]-[Rr]ate[Ll]imit-[Rr]emaining: *\([0-9]*\).*/\1/p' "$1" 2>/dev/null)
  [ "${r:-1}" -gt 0 ]
}

# vc_json_field KEY < json -> first string/number value of KEY (no jq needed)
vc_json_field() {
  tr ',' '\n' | sed -n "s/^[[:space:]{\[]*\"$1\":[[:space:]]*\"\{0,1\}\([^\"]*\)\"\{0,1\}[]}[:space:]]*\$/\1/p" | head -n 1
}

# vc_release_fields JSON -> "tag<TAB>date<TAB>size<TAB>url" (first asset; '-' if none)
vc_release_fields() {
  t=$(vc_json_field tag_name < "$1"); p=$(vc_json_field published_at < "$1")
  s=$(sed -n '/"assets"/,$p' "$1" | vc_json_field size)
  u=$(vc_json_field browser_download_url < "$1")
  printf '%s\t%s\t%s\t%s\n' "${t:--}" "${p:--}" "${s:--}" "${u:--}"
}

# vc_row NAME REPO TAG DATE SIZE URL STATUS -> one TSV line (tabs stripped)
vc_row() {
  out=; for f in "$@"; do f=$(printf '%s' "${f:--}" | tr '\t\n' '  '); out="$out${out:+	}$f"; done
  printf '%s\n' "$out"
}

# vc_build DIR CACHEDIR < names -> full TSV on stdout
vc_build() {
  tmp=${TMPDIR:-/tmp}/vc.$$; vc_classify "$1" > "$tmp"
  vc_repos < "$tmp" | while IFS= read -r r; do vc_fetch "$r" "$2" >/dev/null || :
    vc_rate_ok "$2/$(printf '%s' "$r" | tr '/' '_').hdr" || { echo "vc: rate limit hit" >&2; break; }
  done
  printf '%s\n' "$VC_HEADER"
  while IFS='	' read -r n r; do
    if [ "$r" = - ]; then vc_row "$n" - - - - - unknown; continue; fi
    j="$2/$(printf '%s' "$r" | tr '/' '_').json"
    if [ -s "$j" ] && [ ! -e "$j.err" ]; then
      IFS='	' read -r t p s u <<E
$(vc_release_fields "$j")
E
      vc_row "$n" "$r" "$t" "$p" "$s" "$u" ok
    else vc_row "$n" "$r" - - - - error; fi
  done < "$tmp"; rm -f "$tmp"
}
