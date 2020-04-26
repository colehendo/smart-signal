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
<<<<<<< HEAD
ssh -i ./smart-signal-ec2.pem -tt ec2-user@3.226.158.116 "sudo su aws s3 sync --delete s3://smart-signal/ /var/www/html/"
=======
ssh -i ./smart-signal-frontend.pem -tt ec2-user@3.226.158.116 "sudo aws s3 sync --delete s3://smart-signal/ /var/www/html/"
>>>>>>> 7158c62c1893642d6548ffd63cadd4a6b757c877

echo ""
echo "Site has been updated."