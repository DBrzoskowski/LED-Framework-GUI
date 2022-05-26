# location of qt exe
designer.exe in site-packages -> qt5_applications -> Qt -> bin

# change ui to py
pyuic5 –x v1.ui –o test.py
python -m PyQt5.uic.pyuic -x v1.ui -o test.py


.\venv\Scripts\activate
deactivate


---

klatka_button (start <-> stop - przechowywanie stanu animacji w cache)
klatka_button (zapisz klatka) -> popup input for user - ilosc klatek
fps = stale dla calej animacji
dodatkowo button spectrum (start <-> stop) -> wysylanie animacji na kostke

create animation -> odpala flage draw + clase Cube3D (czyli kostke w przegladarce)
save animation -> zapisanie do pliku .txt
end creating animation -> wylacza flage draw
pasue - out (do wywalenia)
stop - resteuje stan kostki