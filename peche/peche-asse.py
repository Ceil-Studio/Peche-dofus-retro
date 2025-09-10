#!/usr/bin/env python3
from Xlib import display, X
import os
import time
import random
import requests
import math
import struct
import variable
from custom_fonction import send_telegram, capture_region_bmp, send_photo_telegram, search_color, ctrl_double_click_until_color, get_mouse_pixel, get_pixel, search_and_click, search, mousemove, click, click_notransition, move_towards, is_clickable, click_and_update, recherche_pnj, lvl_up, fin_de_combat, en_combat, passe_tour, start_combat


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

mapsposition = [
    (722, 312),
    (297, 478),
    (140, 479),
    (297, 477),
    (510, 477),
    (26, 178),
    (561, 68),
    (297, 72),
    (350, 71),
    (612, 76),
]
resources_positions = {
    1: [
        (614, 75),
        (639, 112),
        (693, 90),
        (720, 154),
    ],
    2: [
        (85, 368),
        (111, 383),
        (165, 381),
        (192, 366),
        (136, 424),
        (324, 436),
        (324, 407),
        (379, 386),
        (453, 424),
        (454, 450),
        (484, 406),
        (510, 454),
    ],
    3: [
        (507, 99),
        (480, 171),
        (456, 207),
        (376, 164),
        (322, 166),
        (324, 220),
        (270, 219),
        (241, 233),
        (296, 287),
        (352, 316),
        (375, 357),
        (322, 354),
        (402, 428),
    ],
    4: [
        (453, 126),
        (507, 126),
        (560, 150),
        (667, 290),
        (616, 450),
    ],
    5: [
        # ➕ ajoute positions pour map 4
        # (349, 477),
    ],
    6: [
        (695, 165),
        (668, 206),
        (533, 195),
        (482, 219),
        (403, 233),
        (323, 245),
        (191, 259),
        (215, 298),

        # ➕ ajoute positions pour map 4
        # (349, 477),
    ],
    7: [
        # ➕ ajoute positions pour map 4
        # (349, 477),
    ],
    8: [
        # ➕ ajoute positions pour map 4
        # (349, 477),
    ],
    9: [
        # ➕ ajoute positions pour map 4
        # (349, 477),
    ],
    10: [
        # ➕ ajoute positions pour map 4
        # (349, 477),
    ],
}

def change_map():

    nb_map = len(mapsposition)
    time.sleep(10)

    x, y = mapsposition[variable.maps-1]

    click(x, y)


    variable.maps = variable.maps+1

    if variable.maps>nb_map:
        variable.maps = 1

    time.sleep(10)



def do_collect():
    print("Collecte en cours...")

    positions = resources_positions[variable.maps][:]
    # random.shuffle(positions)  # mélange aléatoire
    time.sleep(0.5)


    #verif combat 
    pixel_color = get_pixel(720, 460)

    if pixel_color == (255, 102, 0):
        variable.etat="start_combat"
        return

    #verif surpoid
    pixel_color = get_pixel(391, 519)
    if pixel_color == (255, 102, 0):
        variable.etat="retour_banque"
        return
    
    for pos in positions:
        x, y = pos        

        #verif combat
        pixel_color = get_pixel(720, 460)

        if pixel_color == (255, 102, 0):
            variable.etat="start_combat"
            return

        # Clique sur la ressource
        click(x, y)
        offset_x = x+20
        offset_y = y+21
        time.sleep(0.3)  # petit délai pour que l'action soit visible
        
        pixel_color = get_pixel(offset_x, offset_y)

        if pixel_color == (213, 207, 170):
            print(f"🎯 Couleur détectée à {offset_x},{offset_y} | clic effectué")
            click(offset_x, offset_y)
            os.system("xdotool mousemove 0 0")
            
            for i in range(1, variable.temps_recolte):
                #verif combat
                pixel_color = get_pixel(720, 460)

                if pixel_color == (255, 102, 0):
                    variable.etat="start_combat"
                    return

                time.sleep(1)

        else:
            print(f"❌ Couleur non détectée à {offset_x},{offset_y} | retour à la ressource précédente, {pixel_color}")
            # Ici tu peux décider de revenir à la position précédente ou continuer
        #verif combat
        pixel_color = get_pixel(720, 460)

        if pixel_color == (255, 102, 0):
            variable.etat="start_combat"
            return
        #verif lvl_up
        pixel_color = get_pixel(397, 297)

        if pixel_color == (255, 97, 0):
            variable.etat="lvl_up"
            return
    change_map()

def retour_banque():
    timemap = 11
    
    nb_map = len(mapsposition)

    nb_clicks = ((nb_map+1) - variable.maps) % nb_map

    if nb_clicks>0:
        for i in range(nb_clicks):
            change_map()


    print("Retour à la banque...")
    send_telegram("🏦 Le bot retourne à la banque.")
    time.sleep(2)
    click(31, 340)
    time.sleep(timemap)
    click(33, 315)
    time.sleep(timemap)
    click(31, 369)
    time.sleep(timemap)
    click(32, 262)
    time.sleep(timemap)
    click(28, 422)
    time.sleep(timemap)
    click(32, 206)
    time.sleep(timemap)
    click(31, 369)
    time.sleep(timemap)
    click(31, 449)
    time.sleep(timemap)
    click(31, 422)
    time.sleep(timemap)
    click(30, 316)
    time.sleep(timemap)
    click(351, 70)
    time.sleep(timemap)
    click(216, 83)
    time.sleep(timemap)
    click(319, 83)
    time.sleep(timemap)
    click(319, 87)
    time.sleep(timemap)
    click(532, 83)
    time.sleep(timemap)
    click(138, 70)
    time.sleep(timemap)
    click(325, 274)
    time.sleep(timemap)

    variable.etat="recherche_pnj"

def retour_peche():
    timemap = 10
    print("Retour à la pêche...")
    send_telegram("🎣 Le bot retourne à la pêche.")

    time.sleep(1)
    click(162, 328)
    time.sleep(timemap)
    click(562, 473)
    time.sleep(timemap)
    click(400, 473)
    time.sleep(timemap)
    click(348, 476)
    time.sleep(timemap)
    click(348, 476)
    time.sleep(timemap)
    click(302, 474)
    time.sleep(timemap)
    click(346, 476)
    time.sleep(timemap)
    click(723, 315)
    time.sleep(timemap)
    click(722, 423)
    time.sleep(timemap)
    click(722, 476)
    time.sleep(timemap)
    click(722, 366)
    time.sleep(timemap)
    click(722, 232)
    time.sleep(timemap)
    click(723, 423)
    time.sleep(timemap)
    click(717, 288)
    time.sleep(timemap)
    click(720, 423)
    time.sleep(timemap)
    click(721, 314)
    time.sleep(timemap)
    click(721, 314)
    time.sleep(timemap)

    variable.maps = 1

    variable.etat = "collect"

# Mapping état -> fonction
actions = {
    "collect": do_collect,
    "start_combat": start_combat,
    "en_combat": en_combat,
    "fin_de_combat": fin_de_combat,
    "lvl_up": lvl_up,
    "retour_banque": retour_banque,
    "recherche_pnj": recherche_pnj,
    "retour_peche": retour_peche,
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


