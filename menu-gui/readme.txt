# location of qt exe
designer.exe in site-packages -> qt5_applications -> Qt -> bin

# change ui to py
pyuic5 –x v1.ui –o test.py
python -m PyQt5.uic.pyuic -x v1.ui -o test.py


.\venv\Scripts\activate
deactivate
