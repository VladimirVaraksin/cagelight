cd ~ || exit
cd RaspberryPi || git clone https://github.com/VladimirVaraksin/RaspberryPi.git
python3.10 -m venv yolovenv
source yolovenv/bin/activate
pip install -r requirements.txt