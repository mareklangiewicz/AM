# THROWAWAY POSIX awk reader. Schema-shaped, not a general YAML parser.
function fail(message) {
    print "catalog YAML: line " NR ": " message > "/dev/stderr"
    invalid=1; exit 2
}
function less(a,b) { return length(a)<length(b) || (length(a)==length(b) && "x" a < "x" b) }
function uint(s) { return s ~ /^(0|[1-9][0-9]*)$/ && !less("9223372036854775807",s) }
function id(s) { return uint(s) && s!="0" }
function timestamp(s, y,m,d,h,n,t,days) {
    if (length(s)!=20 || s !~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z$/) return 0
    y=substr(s,1,4)+0; m=substr(s,6,2)+0; d=substr(s,9,2)+0
    h=substr(s,12,2)+0; n=substr(s,15,2)+0; t=substr(s,18,2)+0
    days=(m==2 ? 28+(y%4==0 && (y%100!=0 || y%400==0)) : (m==4 || m==6 || m==9 || m==11 ? 30 : 31))
    return y>=1970 && m>=1 && m<=12 && d>=1 && d<=days && h<24 && n<60 && t<60
}
function decode(s, out,i,c,e) {
    if (substr(s,1,1)!="\"" || substr(s,length(s),1)!="\"" || length(s)<2) fail("quoted string required")
    out=""
    for (i=2;i<length(s);i++) {
        c=substr(s,i,1)
        if (c=="\"") fail("unescaped quote")
        if (c=="\\") {
            if (++i>=length(s)) fail("unfinished escape")
            e=substr(s,i,1)
            if (e=="n") c="\n"
            else if (e=="r") c="\r"
            else if (e=="t") c="\t"
            else if (e=="N") c="\302\205"
            else if (e=="L") c="\342\200\250"
            else if (e=="P") c="\342\200\251"
            else if (e=="\"" || e=="\\") c=e
            else fail("unsupported escape")
        }
        out=out c
    }
    return out
}
function rank(context,key, fields,a,n,i) {
    if (context=="root") fields="format schema repository_id repository checked_at check_status check_reason releases apps"
    else if (context=="release") fields="tag title url created_at published_at updated_at prerelease source_zip_url source_tar_url assets"
    else if (context=="asset") fields="name url size content_type digest"
    else return 0
    n=split(fields,a," "); for(i=1;i<=n;i++) if(a[i]==key) return i
    return 0
}
function expect(path,kind) { if(types[slot(path)]!=kind) fail("missing or wrong field: " path) }
function required(path,fields, a,n,i) {
    n=split(fields,a," "); for(i=1;i<=n;i++) if(!(slot(path "/" a[i]) in types)) fail("missing field: " path "/" a[i])
}
function schema_url(s, a,n) {
    n=split(s,a,"/")
    return n==8 && a[1]=="https:" && a[2]=="" && a[3]=="raw.githubusercontent.com" &&
        a[4] ~ /^[A-Za-z0-9-]+$/ && a[5] ~ /^[A-Za-z0-9_.-]+$/ &&
        length(a[6])==40 && a[6] !~ /[^0-9a-f]/ && a[7]=="docs" && a[8]=="catalog-format-v2.md"
}
# Reuse storage keys across records, including on awk implementations that retain
# allocation associated with distinct deleted keys. Full paths remain query facts.
function slot(p, q) {
    q=p
    sub(/\/[0-9]+/,"/@",q); sub(/\/[0-9]+/,"/@",q)
    if(q ~ /^\/apps\//) q="/apps/@"
    return q
}
function finish_record(p, context, k,prefix,i) {
    if (context=="release_ids") required(p,"tag url published_at prerelease assets")
    else required(p,"name url size content_type")
    if (operation=="rows" && parent_path(p)==query) {
        printf "%s",substr(p,length(query)+2)
        for(i=1;i<=field_count;i++) printf "\t%s",encoded[slot(p "/" fields[i])]
        printf "\n"
    }
    prefix=slot(p) "/"
    for(k in types) if(k==slot(p) || index(k,prefix)==1) {
        delete types[slot(k)]; delete values[slot(k)]; delete encoded[slot(k)]; delete children[slot(k)]
        delete last_id[slot(k)]; delete last_order[slot(k)]; delete records[slot(k)]
    }
}
function parent_path(p, q) { q=p; sub(/\/[^\/]*$/,"",q); return q }
function close_nodes(depth, d,p) {
    for(d=previous;d>=depth;d--) {
        p=stack[d]
        if(slot(p) in types && types[slot(p)]=="map" && !children[slot(p)]) fail("use {} for empty mapping")
        if(slot(p) in records) finish_record(p,records[slot(p)])
    }
}
BEGIN {
    operation=ENVIRON["AM_YAML_OPERATION"]; query=ENVIRON["AM_YAML_QUERY"]; previous=-1
    if(operation=="assets") query="/releases" query "/assets"
    if(operation=="releases") query="/releases"
    if(operation=="apps") query="/apps"
    if(operation=="rows") {
        if(query !~ /^\/releases(\/[0-9]+\/assets)?$/) fail("collection path")
        context=(query=="/releases" ? "release" : "asset")
        field_count=split(ENVIRON["AM_YAML_FIELDS"],fields," ")
        for(i=1;i<=field_count;i++) if(!rank(context,fields[i]) || fields[i]=="assets") fail("scalar projection field")
    }
}
{
    bytes+=length($0)+1
    if (bytes>33554432 || length($0)>65536) fail("size limit")
    if ($0 ~ /[[:cntrl:]]/ || $0 ~ /\302[\200-\237]|\342\200[\250\251]|\357\277[\276\277]/ || $0 ~ / $/ || $0=="") fail("control, blank line or trailing space")
    match($0,/^ */); depth=RLENGTH/2
    if (RLENGTH%2 || depth>4 || depth>previous+1) fail("indentation")
    close_nodes(depth)
    line=substr($0,RLENGTH+1); colon=index(line,":")
    if (!colon) fail("missing colon")
    key=substr(line,1,colon-1); raw=substr(line,colon+1)
    quoted=(key ~ /^"[a-z0-9][a-z0-9_.+-]*"$/)
    if (quoted) key=substr(key,2,length(key)-2)
    else if (key !~ /^[a-z][a-z0-9_]*$/) fail("invalid key")
    parent=(depth ? stack[depth-1] : "")
    if (depth && types[slot(parent)]!="map") fail("child of scalar or empty mapping")
    path=parent "/" key
    if (slot(path) in types) fail("duplicate key")
    if (depth==0) context="root"
    else if (depth==1 && parent=="/releases") context="release_ids"
    else if (depth==1 && parent=="/apps") context="app_ids"
    else if (depth==2 && parent ~ /^\/releases\/[0-9]+$/) context="release"
    else if (depth==3 && parent ~ /^\/releases\/[0-9]+\/assets$/) context="asset_ids"
    else if (depth==4 && parent ~ /^\/releases\/[0-9]+\/assets\/[0-9]+$/) context="asset"
    else fail("unsupported nesting")
    if (context=="release_ids" || context=="asset_ids") {
        if (!quoted || !id(key) || (slot(parent) in last_id && !less(last_id[slot(parent)],key))) fail("ID order or spelling")
        last_id[slot(parent)]=key
    } else {
        if (context=="app_ids") {
            if (!quoted) fail("quoted app name required")
            if (slot(parent) in last_id && "x" last_id[slot(parent)] >= "x" key) fail("app order")
            last_id[slot(parent)]=key
        } else {
            if (quoted) fail("unexpected quoted key")
            order=rank(context,key)
            if (!order || order<=last_order[slot(parent)]) fail("unknown or out-of-order field")
            last_order[slot(parent)]=order
        }
    }
    if (raw=="") { kind="map"; value="" }
    else {
        if (substr(raw,1,1)!=" " || substr(raw,2,1)==" ") fail("one space after colon required")
        raw=substr(raw,2)
        if (raw=="{}") { kind="empty"; value="" }
        else if (substr(raw,1,1)=="\"") { kind="string"; value=decode(raw) }
        else if (raw=="true" || raw=="false") { kind="bool"; value=raw }
        else if (uint(raw)) { kind="integer"; value=raw }
        else fail("unsupported scalar")
    }
    if (context=="release_ids" || context=="asset_ids") {
        if (kind!="map") fail("record must be nonempty mapping")
        records[slot(path)]=context
    } else if (context=="app_ids") {
        if (kind!="integer" || !id(value)) fail("repository ID required")
    } else if (key=="releases" || key=="assets" || key=="apps") {
        if (kind!="map" && kind!="empty") fail("mapping required")
    } else if (key=="format" || key=="repository_id" || key=="size") {
        if (kind!="integer" || (key=="format" && value!="2") || (key=="repository_id" && !id(value))) fail("integer field")
    } else if (key=="prerelease") {
        if (kind!="bool") fail("boolean required")
    } else {
        if (kind!="string") fail("string required")
        if (key ~ /_at$/ && !timestamp(value)) fail("timestamp")
        if ((key=="url" || key ~ /^source_.*_url$/) && (value !~ /^https:\/\// || value ~ /[[:space:][:cntrl:]]/)) fail("HTTPS URL")
    }
    types[slot(path)]=kind; values[slot(path)]=value; encoded[slot(path)]=raw; stack[depth]=path; previous=depth
    children[slot(parent)]++
    if(path==query) {
        found=1
        if(operation=="get") {
            if(kind=="map" || kind=="empty") fail("scalar query required")
            printf "%s",value
        }
    }
    if((operation=="releases" || operation=="assets" || operation=="apps") && parent==query) print key
    if(context=="app_ids") { delete types[slot(path)]; delete values[slot(path)]; delete encoded[slot(path)] }
}
END {
    if (invalid) exit 2
    close_nodes(0)
    required("","format schema")
    if (!schema_url(values[slot("/schema")])) fail("immutable schema URL")
    if ("/apps" in types) {
        if (children[slot("")]!=3) fail("app map root fields")
    } else {
        required("","repository_id repository check_status")
        if (values[slot("/repository")] !~ /^[A-Za-z0-9-]+\/[A-Za-z0-9_.-]+$/) fail("repository name")
        state=values[slot("/check_status")]
        if (state!="ok" && state!="failed") fail("check status")
        if (("/releases" in types) != ("/checked_at" in types)) fail("observation/check time pairing")
        if (state=="ok") {
            required("","checked_at releases")
            if ("/check_reason" in types) fail("reason on successful check")
        } else {
            required("","check_reason")
            if (values[slot("/check_reason")] !~ /^(rate_limited|transport|invalid_response|collection_limit)$/) fail("check reason")
        }
    }
    if(operation=="validate") exit 0
    if(!found) exit 3
    exit 0
}
