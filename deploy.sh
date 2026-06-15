#!/bin/sh
# Deploy the House of Naqash site to Cloudways via SFTP.
#
# Usage:            ./deploy.sh
# Override target:  CW_USER=... CW_HOST=... ./deploy.sh
#
# The app user is SFTP-only (no shell), so this drives `sftp` with a
# batch file. You'll be prompted for the SFTP password.
#
# NOTE: data/products.json is NOT uploaded — the copy on the server is the
# live catalogue, managed through admin.php. Overwriting it would discard
# products added there. To re-seed it deliberately:
#   echo 'put data/products.json data/products.json' | sftp hon_ftp@139.59.89.163:public_html
set -eu

CW_USER="${CW_USER:-hon_ftp}"
CW_HOST="${CW_HOST:-139.59.89.163}"

cd "$(dirname "$0")"
python3 build.py
rm -rf dist && mkdir dist
cp -R index.html cushions.html fabrics.html rugs.html throws.html contact.html admin.php css js images dist/
cp .htaccess.template dist/.htaccess

BATCH="$(mktemp)"
cat > "$BATCH" <<EOF
cd public_html
lcd "$(pwd)/dist"
put .htaccess
put index.html
put cushions.html
put fabrics.html
put rugs.html
put throws.html
put contact.html
put admin.php
-mkdir css
put css/style.css css/style.css
-mkdir js
put js/main.js js/main.js
-mkdir images
put images/* images/
EOF

echo "Deploying to $CW_USER@$CW_HOST:public_html ..."
sftp -o BatchMode=no -b "$BATCH" "$CW_USER@$CW_HOST"
rm -f "$BATCH"
echo "Done. Open the app URL to verify."
