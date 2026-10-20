#!/bin/sh
# stub curl: honours -o, -D, If-None-Match; logs args to $STUB_LOG
out=; hdr=; inm=
while [ $# -gt 0 ]; do case $1 in -o) out=$2; shift;; -D) hdr=$2; shift;;
  -H) case $2 in If-None-Match:*) inm=1;; esac; shift;; esac; shift; done
echo "call inm=${inm:-0}" >> "$STUB_LOG"
if [ -n "$STUB_FAIL" ]; then printf 'x-ratelimit-remaining: 0\r\n' > "$hdr"; printf 403; exit 0; fi
if [ -n "$inm" ]; then printf 'ETag: "e1"\r\nx-ratelimit-remaining: 50\r\n' > "$hdr"; printf 304; exit 0; fi
cp "$STUB_JSON" "$out"; printf 'ETag: "e1"\r\nx-ratelimit-remaining: 50\r\n' > "$hdr"; printf 200
