#!/usr/bin/env bash
# Native Linux syntax validation only; no service installation/start or secrets.
set -euo pipefail
repo=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d)
trap 'rm -rf -- "$work"' EXIT
openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj /CN=example.invalid -keyout "$work/key.pem" -out "$work/cert.pem" 2>/dev/null
sed -e "s|listen 443 ssl;|listen 127.0.0.1:14443 ssl;|" -e "s|/etc/interview-prep/tls/fullchain.pem|$work/cert.pem|" -e "s|/etc/interview-prep/tls/privkey.pem|$work/key.pem|" "$repo/deploy/single-vm/nginx.conf" > "$work/site.conf"
printf 'pid %s/nginx.pid;\nerror_log stderr;\nevents {}\nhttp { include %s/site.conf; }\n' "$work" "$work" > "$work/nginx.conf"
nginx -t -p "$work/" -c "$work/nginx.conf"
# Host-specific users, paths and secrets are intentionally substituted for syntax QA.
for unit in ipa-api ipa-web; do
  sed -e 's|^User=.*|User=root|' -e 's|^Group=.*|Group=root|' -e 's|^WorkingDirectory=.*|WorkingDirectory=/tmp|' -e '/^EnvironmentFile=/d' -e 's|^ExecStart=.*|ExecStart=/usr/bin/true|' "$repo/deploy/single-vm/$unit.service" > "$work/$unit.service"
done
systemd-analyze verify "$work/ipa-api.service" "$work/ipa-web.service"
echo 'nginx and systemd syntax passed; host paths, readiness and live traffic remain unverified'
