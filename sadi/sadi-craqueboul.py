#!/usr/bin/env python3
from Xlib import display, X
import os
import time
import random
import requests
import math
import struct
import variable
from custom_fonction import send_telegram, capture_region_bmp, send_photo_telegram, search_color, ctrl_double_click_until_color, get_mouse_pixel, get_pixel, search_and_click, search, mousemove, click, click_notransition, move_towards, is_clickable, click_and_update, recherche_pnj, lvl_up, en_combat, passe_tour, start_combat, rclick, search_and_lclick, detruit_ressources

folder = "./telegram"
print("DEBUG: contenu du dossier :", os.listdir(folder))
# récupère le premier fichier du dossier
filename = os.listdir(folder)[0]
CHAT_ID = os.path.splitext(filename)[0]
filepath = os.path.join(folder, filename)
with open(filepath, "r") as f:
    TOKEN = f.read().strip()

URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

print(f"token : {TOKEN} CHAT : {CHAT_ID}")

send_telegram("🚀 Bot lancé sur le VPS !")

# Initialisation X11
dsp = display.Display()
root = dsp.screen().root

couleur_monstre = (79, 83, 53)
map_id = None

def map_1_2():
    time.sleep(0.5)
    click(718, 311)
    for i in range (200):
        time.sleep(0.2)
        pixel_color = get_pixel(361, 343)
        if pixel_color == (185, 174, 154):
            return

def map_2_3():
    time.sleep(0.5)
    click(239, 475)
    for i in range (200):
        time.sleep(0.2)
        pixel_color = get_pixel(241, 349)
        if pixel_color == (74, 25, 2):
            return

def map_3_2():
    time.sleep(0.5)
    click(295, 68)
    for i in range (200):
        time.sleep(0.2)
        pixel_color = get_pixel(361, 343)
        if pixel_color == (185, 174, 154):
            return

def map_2_1():
    time.sleep(0.5)
    click(29,312)
    for i in range (200):
        time.sleep(0.2)
        pixel_color = get_pixel(626, 244)
        if pixel_color == (142, 126, 102):
            return

def tremblement():
    rclick(533, 553)

def ventempoi():
    rclick(560, 553)

def puissancesyl():
    rclick(591, 553)

def verif_combat():
    pixel_color = get_pixel(731, 429)
    if pixel_color == (225, 30, 27):
        variable.etat="start_combat"
        return True
    return False

def verif_surpoid():
    pixel_color = get_pixel(391, 519)
    if pixel_color == (255, 102, 0):
        variable.etat="retour_banque"
        return True
    return False

def mange_pain():
    for _ in range(8):
        click(539, 581)
        time.sleep(0.05)
        click(539, 581)
        time.sleep(0.05)
    click(505, 554)

def lanceur_de_combat():
    global map_id
    print("Xp en cours...")
    box = (0, 0, 750, 620)

    while variable.etat == "collect":
        # quick check at loop start
        if verif_surpoid() or verif_combat():
            return  # let main() dispatch to the new state's function

        map_id = 1
        for _ in range(3):
            time.sleep(0.1)
            search_and_click(box, couleur_monstre)
            time.sleep(5)
            if verif_combat():
                return
        print("Deplacement: map 1 --> 2")
        map_1_2()
        map_id = 2
        for _ in range(3):
            time.sleep(0.1)
            search_and_click(box, couleur_monstre)
            time.sleep(5)
            if verif_combat():
                return
        print("Deplacement: map 2 --> 3")
        map_2_3()
        map_id = 3
        for _ in range(3):
            time.sleep(0.1)
            search_and_click(box, couleur_monstre)
            time.sleep(5)
            if verif_combat():
                return
        print("Deplacement: map 3 --> 2")
        map_3_2()
        map_id = 2
        for _ in range(3):
            time.sleep(0.1)
            search_and_click(box, couleur_monstre)
            time.sleep(5)
            if verif_combat():
                return
        print("Deplacement: map 2 --> 1")
        map_2_1()
        time.sleep(0.2)
        mange_pain()
        detruit_ressources()
    return

def check_fin_combat():
    for _ in range(100):
       time.sleep(0.5)
       pixel_color = get_pixel(441, 515)
       if pixel_color == (255, 102, 0):
           return False
       box = (570, 380, 10, 90)
       target_color = (255, 97, 0)
       found = search_and_lclick(box, target_color)
       if found:
           print("✅ Action effectuée.")
           variable.etat = "collect"
           return True
    return False       

def detect_map_id():
    if get_pixel(361, 343) == (185, 174, 154):
        return 2
    if get_pixel(241, 349) == (74, 25, 2):
        return 3
    if get_pixel(626, 244) == (142, 126, 102):
        return 1
    return None

def combat_sadi():
    global map_id
    print("Démarrage du combat...")
    time.sleep(2)
    map_id = detect_map_id()
    print("Map: ", map_id)

    # Placement sur la map
    if map_id == 1:
        click(319, 273)
        time.sleep(1)
        click(397, 313) 
    if map_id == 2:
        click(318, 271)
        time.sleep(1)
        click(425, 220)
    if map_id == 3:
        click(400, 258)
        time.sleep(1)
        click(507, 312)            
    time.sleep(1)
    click(720, 460)
    time.sleep(0.3)
    os.system("xdotool mousemove 535 526")
    time.sleep(2.5)

    print("T1 commence")
    tremblement()
    ventempoi()
    tremblement()
    ventempoi()
    puissancesyl()
    passe_tour()
    print("T1 fin")

    while True:
        pixel_color = get_pixel(441, 515)
        if pixel_color == (255, 102, 0):
            break
        time.sleep(0.3)

    print("T2 commence")
    puissancesyl()
    puissancesyl()
    passe_tour()
    print("T2 fin")

    if check_fin_combat(): return

    print("T3 commence")
    passe_tour()
    print("T3 fin")

    if check_fin_combat(): return

    print("T4 commence")
    passe_tour()
    print("T4 fin")

    if check_fin_combat(): return

    print("T5 commence")
    passe_tour()
    print("T5 fin")

    check_fin_combat()

    return    

# Mapping état -> fonction
actions = {
    "collect": lanceur_de_combat,
    "start_combat": combat_sadi,
    "en_combat": en_combat,
    "lvl_up": lvl_up,
}

def main():
    print("🔎 Bot démarré. Ctrl+C pour quitter.")
    while True:
        try:

            pos, color = get_mouse_pixel()
            x, y = pos
            print(f"État: {variable.etat} | Position: {x},{y} | Couleur: {color}", end="\r")

            # Appel de la fonction correspondant à l'état
            if variable.etat in actions:
                actions[variable.etat]()  # exécutera la fonction associée

            # Ici tu pourras ajouter la logique pour passer d'un état à un autre
            # Exemple simple :
            # if variable.etat == "collect" and condition:
            #     variable.etat = "start_combat"

            time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n🔴 Bot arrêté.")
            break

if __name__ == "__main__":
    main()


