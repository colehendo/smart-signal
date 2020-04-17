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
echo "Updating files on EC2..."
echo ""
ssh -i ./smart-signal-frontend.pem -tt ec2-user@3.226.158.116 "sudo aws s3 sync s3://smart-signal/ /var/www/html/"

echo ""
echo "Site has been updated."