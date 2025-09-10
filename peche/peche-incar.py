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
        (612, 475),
        (30, 418),
        (134, 65),
        (720, 123),
]
resources_positions = {
    1: [
        (31, 232),
        (84, 233),
        (216, 246),
        (271, 248),
        (348, 285),
        (344, 315),
        (376, 356),
        (400, 394),
        (434, 411),
    ],
    2: [
        (433, 82),
        (424, 112),
        (482, 161),
        (510, 177),
        (507, 205),
        (477, 244),
        (430, 274),
        (399, 287),
        (378, 327),
        (351, 340),
        (271, 359),
        (217, 379),
        (162, 381),
        (136, 368),
        (81, 343),
    ],
    3: [
        (692, 324),
        (667, 339),
        (639, 356),
        (588, 380),
        (529, 383),
        (482, 352),
        (400, 339),

    ],
    4: [
        (346, 444),
        (320, 406),
        (268, 381),
        (268, 353),
        (268, 327),
        (292, 261),
        (324, 245),
        (480, 191),
        (609, 178),
        (640, 196),
        (668, 208),
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
    click(723, 259)
    time.sleep(timemap)
    click(722, 341)
    time.sleep(timemap)
    click(506, 191)
    click(535, 203)
    click(161, 260)
    time.sleep(timemap)
    click(296, 475)
    time.sleep(timemap)
    click(407, 475)
    time.sleep(timemap)
    click(349, 477)
    time.sleep(timemap)
    click(401, 473)
    time.sleep(timemap)
    click(29, 288)
    time.sleep(timemap)
    click(30, 292)
    time.sleep(timemap)
    click(630, 180)
    time.sleep(timemap)
    variable.etat="recherche_pnj"


def retour_peche():
    timemap = 10
    print("Retour à la pêche...")
    send_telegram("🎣 Le bot retourne à la pêche.")

    time.sleep(1)
    click(218, 409)
    time.sleep(timemap)
    click(32, 290)
    time.sleep(timemap)
    click(509, 269)
    click(565, 303)
    time.sleep(timemap)
    click(30, 449)
    time.sleep(timemap)
    click(30, 368)
    time.sleep(timemap)
    click(512, 474)
    time.sleep(timemap)
    click(639, 463)
    time.sleep(timemap)
    click(722, 476)
    time.sleep(timemap)
    click(723, 421)
    time.sleep(timemap)
    click(721, 312)
    time.sleep(timemap)
    click(721, 289)
    time.sleep(timemap)
    click(720, 398)
    time.sleep(timemap)
    click(723, 423)
    time.sleep(timemap)
    click(346, 475)
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


