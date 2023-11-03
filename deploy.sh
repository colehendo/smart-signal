#!/bin/bash
set -e

echo ""
echo "Compressing files..."
echo ""
ng build --prod

echo ""
echo "Updating S3 bucket..."
echo ""
aws s3 sync --delete ./dist/smart-signal s3://smart-signal --profile smart-signal-sls

echo ""
echo "Site has been updated."
