# Script to start the production server

# Copy files to production
cp -r * /home/nova-prod

# Copy env file to production
cp env/.prod.env /home/nova-prod/.env

# Change directory
cd /home/nova-prod

# Start screen
screen -S nova-api python run prod
