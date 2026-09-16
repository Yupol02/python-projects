import os

def clean_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[H\033[J",end ="",flush=True)


def kullanici_bakiyesi(bakiye: int):
    print(f"Güncel bakiyeniz: {bakiye} TL")