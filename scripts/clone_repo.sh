cd ~ || exit
cd CageLight || git clone https://github.com/VladimirVaraksin/cagelight.git
python3.10 -m venv yolovenv
source yolovenv/bin/activate
pip install -r requirements.txt