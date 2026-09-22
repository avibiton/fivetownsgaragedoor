#!/bin/bash
# Redirect tests against an Apache server serving ./site with the production .htaccess.
#   tools/test_redirects.sh http://localhost:8787      (local Apache; Host header simulates the real domain)
#   tools/test_redirects.sh                           (defaults to the live domain)
# Each case: request URL + Host header + optional X-Forwarded-Proto  -> expected status and Location.
BASE="${1:-}"
pass=0; fail=0

check() { # name host proto path expected_status expected_location
  local name="$1" host="$2" proto="$3" path="$4" want_status="$5" want_loc="$6"
  local url hdrs=()
  if [ -n "$BASE" ]; then
    url="$BASE$path"; hdrs=(-H "Host: $host")
    [ "$proto" = "https" ] && hdrs+=(-H "X-Forwarded-Proto: https")
  else
    url="$proto://$host$path"
  fi
  local out status loc
  out=$(curl -s -o /dev/null -D - "${hdrs[@]}" "$url")
  status=$(echo "$out" | head -1 | awk '{print $2}')
  loc=$(echo "$out" | awk 'tolower($1)=="location:"{print $2}' | tr -d '\r')
  if [ "$status" = "$want_status" ] && [ "$loc" = "$want_loc" ]; then
    echo "PASS  $name  -> $status ${loc}"; pass=$((pass+1))
  else
    echo "FAIL  $name  -> got $status '${loc}', want $want_status '${want_loc}'"; fail=$((fail+1))
  fi
}

D=fivetownsgaragedoor.com
W=www.fivetownsgaragedoor.com
F=https://fivetownsgaragedoor.com

# Legacy retired URLs: single hop from ANY scheme/host to the final canonical URL
check "https /contact.php"            $D https /contact.php 301 "$F/contact.html"
check "http /contact.php"             $D http  /contact.php 301 "$F/contact.html"
check "http www /contact.php"         $W http  /contact.php 301 "$F/contact.html"
check "https /error.html"             $D https /error.html  301 "$F/index.html"
check "http www /error.html"          $W http  /error.html  301 "$F/index.html"
# Protocol / host normalization preserves the path (single hop)
check "http root"                     $D http  /            301 "$F/"
check "http /repair.html"             $D http  /repair.html 301 "$F/repair.html"
check "http www /Genieopeners.html"   $W http  /Genieopeners.html 301 "$F/Genieopeners.html"
check "https www /LocationServices"   $W https /LocationServices.html 301 "$F/LocationServices.html"
check "https www root"                $W https /            301 "$F/"
check "http query string kept"        $D http  "/faq.html?x=1" 301 "$F/faq.html?x=1"
# Canonical host over HTTPS: served directly, no redirect (no loop between / and /index.html)
check "https /"                       $D https /            200 ""
check "https /index.html"             $D https /index.html  200 ""
for p in cedarhurst-garage-door.html commercial.html contact.html faq.html Genieopeners.html \
         hewlett-garage-door.html installation.html inwood-garage-door.html lawrence-garage-door.html \
         liftmasteropeners.html LocationServices.html openers.html repair.html residential.html \
         woodmere-garage-door.html; do
  check "https /$p" $D https "/$p" 200 ""
done
check "https /sitemap.xml"            $D https /sitemap.xml 200 ""
check "https /robots.txt"             $D https /robots.txt  200 ""
check "https missing page is 404"     $D https /nope.html   404 ""
# Linux hosting is case-sensitive; macOS dev filesystems are not, so only test this live.
[ -z "$BASE" ] && check "case-sensitive (no /genieopeners.html)" $D https /genieopeners.html 404 ""

echo; echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
