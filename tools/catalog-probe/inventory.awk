# Textual discovery only: never evaluate a recipe or expand its variables.
BEGIN {
    OFS = "\t"
    print "file", "line", "context", "url", "classification", "repository", "endpoint"
    print "file", "version_lines", "version_lines_differ", "api_occurrences" > scripts
}
FNR == 1 {
    flush()
    file = FILENAME
    first = ""
    versions = differs = occurrences = 0
}
{
    line = $0
    sub(/^[[:space:]]+/, "", line)
    sub(/[[:space:]]+$/, "", line)
    if (line ~ /^version=/) {
        versions++
        if (versions == 1) first = line
        else if (line != first) differs = 1
    }
    context = line ~ /^#/ ? "comment" : "code"
    rest = $0
    while (match(rest, /https:\/\/api[.]github[.]com[^[:space:]|<>;]*/)) {
        url = substr(rest, RSTART, RLENGTH)
        rest = substr(rest, RSTART + RLENGTH)
        # Quotes delimit shell words, not URL bytes. Variables remain unresolved.
        gsub(/["\047]/, "", url)
        sub(/[)]+$/, "", url)
        classification = "unresolved"
        repo = endpoint = "-"
        if (url ~ /[$`\\]/) classification = "dynamic"
        else if (url ~ /\/REPLACETHIS\//) classification = "template-placeholder"
        else if (url ~ /^https:\/\/api[.]github[.]com\/repos\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+(\/|$)/) {
            path = url
            sub(/^https:\/\/api[.]github[.]com\/repos\//, "", path)
            split(path, parts, "/")
            repo = tolower(parts[1] "/" parts[2])
            endpoint = path
            sub(/^[^/]+\/[^/]+\/?/, "", endpoint)
            if (endpoint == "releases" || endpoint ~ /^releases\?/) classification = "release-list"
            else if (endpoint == "releases/latest" || endpoint ~ /^releases\/latest\?/) classification = "release-latest"
            else if (endpoint ~ /^releases\/tags\//) classification = "release-tag"
            else if (endpoint == "events" || endpoint ~ /^events\?/) classification = "events"
            else classification = "other-repository-api"
        }
        print FILENAME, FNR, context, url, classification, repo, endpoint
        if (context == "code") occurrences++
    }
}
END { flush() }
function flush() {
    if (file != "") print file, versions, differs, occurrences > scripts
}
