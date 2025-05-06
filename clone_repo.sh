cd ~ || exit
git clone https://github.com/VladimirVaraksin/RasberryPi.git
cd RasberryPi || exit
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt   # falls vorhanden
