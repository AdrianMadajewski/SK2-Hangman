# Gra sieciowa Hangman!

Zaliczenie projektu z laboratoriow Sieci Komputerowych 2.

Wykonawcy:

- [Michal Kwarta](https://github.com/MichalKwarta) nr indeksu 1145192
- [Adrian Madajewski](https://github.com/AdrianMadajewski) nr indeksu 145406

# URUCHOMIENIE

- ## Klient

    **WYMAGANIA** PyQt w wersji 5.

    **KONFIGURACJA I URUCHOMIENIE:**

    Nalezy dostosowac zawartosc pliku konfiguracyjnego config.txt z katalogu klienta.

    ***config.txt:***

        adres_ip (np 127.0.0.1)
        nr_portu (np. 2022)

    Uruchomienie klienta:

        cd SK2-Hangman/Client
        python3 main.py

- ## Serwer

    **WYMAGANIA**: Kompilator g++ z mozliwoscia komplilacji przy uzyciu standardu C++17

    **KONFIGURACJA I URUCHOMIENIE:**

    Nalezy tak samo jak w przypadku klienta dostosowac plik config.cfg
    z katalogu serwera. 

    ***config.cfg:***

        adres_ip (np. 127.0.0.1)
        nr_portu (np. 2022)
        words.txt (plik z slowami do gry - odzielany znakiem nowej linii)
    
    Uruchomienie serwera:

        cd SK2-Hangman/Server
        make compile
        make run
    
    Alternatywnie z katalogu serwera: (po kompilacji - inny plik konfiguracyjny)

        ./server new_config.cfg


