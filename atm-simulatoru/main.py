import os
import time
from islemler import karsilama , menu

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[H\033[J",end ="",flush=True)

def main():
    clear()
    print("=" * 40 )
    print("ATM SİMÜLATÖRÜNE HOŞ GELDİNİZ")
    print("=" * 40 )
    time.sleep(2)
    karsilama()
    print("=" * 40 )
    menu()

if __name__ == '__main__':
    main()



