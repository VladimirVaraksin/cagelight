cd ~ || exit
mkdir CageLight
cd CageLight || exit
git clone https://github.com/THA-CageLight/AI--Realtime.git
python3.12 -m venv yolovenv
source yolovenv/bin/activate
# Install dependencies
sudo apt update
sudo apt install libpq-dev python3-dev
pip install -r requirements.txt