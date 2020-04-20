#!/bin/bash
set -e

echo ""
echo "Compressing files..."
echo ""
ng build --prod

echo ""
echo "Updating S3 bucket..."
echo ""
aws s3 sync --delete dist/smart-signal s3://smart-signal --profile smart-signal

echo ""
echo "Updating files on EC2..."
echo ""
ssh -i ./smart-signal-ec2.pem -tt ec2-user@3.226.158.116 "sudo su aws s3 sync --delete s3://smart-signal/ /var/www/html/"

echo ""
echo "Site has been updated."