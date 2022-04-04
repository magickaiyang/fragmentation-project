# setup wrk, needs to be built from source :(
sudo apt update
sudo apt-get install build-essential libssl-dev git -y

cd client
git clone https://github.com/wg/wrk.git wrk
cd wrk
sudo make
# add to so visible by PATH
sudo cp wrk /usr/local/bin

echo " "
echo "wrk setup done"

