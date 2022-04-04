
# install and setup nginx with homepage workload
sudo apt update
sudo apt install nginx

sudo mkdir -p /var/www/html
sudo cp server/index.html /var/www/html

sudo cp server/conf /etc/nginx/sites-enabled

sudo service nginx restart

echo " "
echo "nginx setup done: now go to localhost:81 in your local browser"
