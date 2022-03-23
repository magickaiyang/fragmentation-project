
# install and setup nginx with homepage workload
sudo apt update
sudo apt install nginx

sudo mkdir -p /var/www/html
sudo cp server/index.html /var/www/html

sudo cp server/conf  /etc/nginx/sites-enabled

sudo service nginx restart

echo " "
echo "nginx setup done: now go to localhost:81 in your local browser"

# setup wrk, needs to be built from source :(
sudo apt-get install build-essential libssl-dev git -y
git clone https://github.com/wg/wrk.git wrk

cd wrk
sudo make
# add to so visible by PATH
sudo cp wrk /usr/local/bin

echo " "
echo "wrk setup done, you can run test.sh now"
