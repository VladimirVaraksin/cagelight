cd ~ || exit
cd RasberryPi || git clone https://github.com/VladimirVaraksin/RasberryPi.git
python3.10 -m venv yolovenv
source yolovenv/bin/activate
pip install -r requirements.txt