#!/bin/bash
set -e

echo "Compressing files..."
ng build --prod

echo "Updating S3 bucket..."
aws s3 sync --delete dist/smart-signal s3://smart-signal --profile smart-signal

echo "Logging onto EC2 instance..."
ssh -i ./smart-signal-ec2.pem ec2-user@54.196.101.72

# echo "Updating EC2 files..."
# sudo aws s3 sync --delete s3://smart-signal/ /var/www/html/

# echo "Logging out of EC2 instance..."
# logout

# echo "Site has been updated."