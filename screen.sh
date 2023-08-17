# Script to start the production server

# Commit to the production branch
git commit -am "Auto-trigger - Production server started" && git push origin Production

# Copy files to production
cp -r * /home/nova-prod

# Copy env file to production
cp env/.prod.env /home/nova-prod/.env

# Change directory
cd /home/nova-prod

# Start screen
screen -S nova-api python run prod
