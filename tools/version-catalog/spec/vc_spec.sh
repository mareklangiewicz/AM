# shellcheck shell=sh
Include lib/vc.sh

Describe 'vc_repo_of'
  It 'extracts repo from /releases'
    When call vc_repo_of 'version=$(curl https://api.github.com/repos/aristocratos/btop/releases | x)'
    The output should eq 'aristocratos/btop'
  End
  It 'extracts repo from /releases/latest with dots'
    When call vc_repo_of 'curl https://api.github.com/repos/foo/bar.app/releases/latest'
    The output should eq 'foo/bar.app'
  End
  It 'is empty for non-github'
    When call vc_repo_of 'curl https://example.org/x'
    The output should eq ''
  End
End

Describe 'vc_endpoint_of'
  Parameters
    'https://api.github.com/repos/a/b/releases/latest' latest
    'https://api.github.com/repos/a/b/releases' list
    'https://x.org' ''
  End
  It "classifies $1"
    When call vc_endpoint_of "$1"
    The output should eq "$2"
  End
End

Describe 'vc_version_line'
  It 'returns first version= line'
    When call vc_version_line "$FIX/x86_64/btop"
    The output should start with 'version=$(curl'
  End
  It 'fails without one'
    When call vc_version_line "$FIX/x86_64/missing"
    The status should be failure
  End
End

Describe 'vc_names'
  It 'parses app list'
    Data:expand
      #|◆ a : x
      #|◆ b : y
    End
    When call vc_names
    The output should eq "a
b"
  End
End

Describe 'vc_classify and vc_repos'
  It 'classifies fixtures'
    Data:expand
      #|btop
      #|other
    End
    When call vc_classify "$FIX/x86_64"
    The line 1 should eq 'btop	aristocratos/btop'
    The line 2 should eq 'other	-'
  End
  It 'dedups repos'
    Data:expand
      #|a	o/r
      #|b	o/r
      #|c	-
      #|d	a/b
    End
    When call vc_repos
    The output should eq "a/b
o/r"
  End
End

Describe 'vc_row'
  It 'joins with tabs and fills empties'
    When call vc_row n r '' d
    The output should eq 'n	r	-	d'
  End
  It 'strips embedded tabs'
    When call vc_row "a	b" c
    The output should eq 'a b	c'
  End
End

Describe 'vc_release_fields'
  It 'reads tag, date, first asset'
    When call vc_release_fields "$FIX/release.json"
    The output should eq 'v1.2	2026-10-01T10:00:00Z	12345	https://github.com/o/r/releases/download/v1.2/a.AppImage'
  End
End

Describe 'vc_fetch cache'
  setup() { C=$(mktemp -d); STUB_LOG=$C/log; STUB_JSON=$FIX/release.json; STUB_FAIL=
    VC_CURL=$FIX/curl_stub.sh; export STUB_LOG STUB_JSON STUB_FAIL; }
  cleanup() { rm -rf "$C"; }
  BeforeEach setup
  AfterEach cleanup
  It 'stores body and etag, then sends If-None-Match'
    vc_fetch o/r "$C" >/dev/null; vc_fetch o/r "$C" >/dev/null
    When call cat "$C/log" "$C/o_r.etag"
    The output should eq 'call inm=0
call inm=1
"e1"'
  End
  It 'keeps cached body on 304'
    vc_fetch o/r "$C" >/dev/null
    When call vc_fetch o/r "$C"
    The output should eq "$C/o_r.json"
    The contents of file "$C/o_r.json" should include 'v1.2'
  End
  It 'fails and records error'
    STUB_FAIL=1
    When call vc_fetch o/r "$C"
    The status should be failure
    The contents of file "$C/o_r.json.err" should eq 403
  End
  It 'vc_rate_ok detects exhaustion'
    STUB_FAIL=1; vc_fetch o/r "$C" || :
    When call vc_rate_ok "$C/o_r.hdr"
    The status should be failure
  End
End

Describe 'vc_build output format'
  setup() { C=$(mktemp -d); STUB_LOG=$C/log; STUB_JSON=$FIX/release.json; STUB_FAIL=
    VC_CURL=$FIX/curl_stub.sh; export STUB_LOG STUB_JSON STUB_FAIL; }
  BeforeEach setup
  AfterEach 'rm -rf "$C"'
  It 'produces header and 7-column rows'
    out() { vc_names < "$FIX/x86_64-apps" | vc_build "$FIX/x86_64" "$C"; }
    When call out
    The line 1 should eq '#name	repo	tag	date	size	url	status'
    The line 2 should eq 'btop	aristocratos/btop	v1.2	2026-10-01T10:00:00Z	12345	https://github.com/o/r/releases/download/v1.2/a.AppImage	ok'
    The line 4 should eq 'other	-	-	-	-	-	unknown'
    The line 5 should eq 'missing	-	-	-	-	-	unknown'
    The lines of output should eq 5
  End
  It 'every row has 7 fields'
    out() { vc_names < "$FIX/x86_64-apps" | vc_build "$FIX/x86_64" "$C" | awk -F'\t' 'NF!=7' | wc -l; }
    When call out
    The output should eq 0
  End
  It 'makes one request per unique repo'
    vc_names < "$FIX/x86_64-apps" | vc_build "$FIX/x86_64" "$C" >/dev/null
    When call grep -c call "$C/log"
    The output should eq 2
  End
End
