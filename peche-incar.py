#!/usr/bin/env python3
from Xlib import display, X
import os
import time
import random
import requests
import math
import struct
from custom_fonction import capture_region_bmp, send_photo_telegram, search_color, ctrl_double_click_until_color, get_mouse_pixel, get_pixel, search_and_click, search, mousemove, click, click_notransition, move_towards, is_clickable, click_and_update, change_map

folder = "./telegram"
print("DEBUG: contenu du dossier :", os.listdir(folder))
# récupère le premier fichier du dossier
filename = os.listdir(folder)[0]
CHAT_ID = os.path.splitext(filename)[0]
filepath = os.path.join(folder, filename)
with open(filepath, "r") as f:
    TOKEN = f.read().strip()

URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

def send_telegram(msg):
    requests.post(URL, data={"chat_id": CHAT_ID, "text": msg})

print(f"token : {TOKEN} CHAT : {CHAT_ID}")

send_telegram("🚀 Bot lancé sur le VPS !")

# Initialisation X11
dsp = display.Display()
root = dsp.screen().root

# Etat initial
etat = "collect"
maps = 1
first_tour = True

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
        (428, 84),
        (428, 112),
        (482, 167),
        (508, 178),
        (507, 206),
        (478, 248),
        (428, 273),
        (400, 286),
        (375, 326),
        (345, 178),
        
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






def do_collect():
    global etat
    global maps
    print("Collecte en cours...")

    positions = resources_positions[maps][:]
    # random.shuffle(positions)  # mélange aléatoire
    time.sleep(0.5)


    #verif combat 
    pixel_color = get_pixel(720, 460)

    if pixel_color == (255, 102, 0):
        etat="start_combat"
        return

    #verif surpoid
    pixel_color = get_pixel(391, 519)
    if pixel_color == (255, 102, 0):
        etat="retour_banque"
        return
    
    for pos in positions:
        x, y = pos        

        #verif combat
        pixel_color = get_pixel(720, 460)

        if pixel_color == (255, 102, 0):
            etat="start_combat"
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
            
            for i in range(1, 30):
                #verif combat
                pixel_color = get_pixel(720, 460)

                if pixel_color == (255, 102, 0):
                    etat="start_combat"
                    return

                time.sleep(1)

        else:
            print(f"❌ Couleur non détectée à {offset_x},{offset_y} | retour à la ressource précédente, {pixel_color}")
            # Ici tu peux décider de revenir à la position précédente ou continuer
        #verif combat
        pixel_color = get_pixel(720, 460)

        if pixel_color == (255, 102, 0):
            etat="start_combat"
            return
        #verif lvl_up
        pixel_color = get_pixel(397, 297)

        if pixel_color == (255, 97, 0):
            etat="lvl_up"
            return
    change_map()

def start_combat():
    global etat
    global positionstartx, positionstarty
    global first_tour
    print("Démarrage du combat...")

    #verif mode tactic

    pixel_color = get_pixel(651, 431)
    if pixel_color != (0,153, 0):
        click(651, 435)

    #verouille combat
    pixel_color = get_pixel(673, 437)
    if pixel_color != (0,153,0):
        click(673, 437)

    #position depart
    box = (7, 58, 730, 400)
    target_color = (255, 0, 0)
    positionstartx, positionstarty = search(box, target_color)
    pixel_color = get_pixel(634, 314)
    time.sleep(0.3)
    click(positionstartx, positionstarty)

    time.sleep(0.5)

    click(720, 460)
    time.sleep(0.3)
    os.system("xdotool mousemove 342 262")
    time.sleep(1)
    etat = "en_combat"
    first_tour = True
    send_telegram("⚔️ Début combat !")

def passe_tour():
    os.system("xdotool key F1")
    time.sleep(1)

def en_combat():
    global etat
    global positionstartx, positionstarty
    global first_tour
    print("Combat en cours...")

    #verif fin
    box = (570, 380, 10, 90)
    target_color = (255, 97, 0)
    found = search_and_click(box, target_color)
    if found:
        print("✅ Action effectuée.")
        etat = "fin_de_combat"
        return



    #verif tour
    pixel_color = get_pixel(441, 515)
    time.sleep(0.3)

    if pixel_color == (255,102,0):
        #tour en cours

        if first_tour:
            first_tour = False

            #mode tactic
            pixel_color = get_pixel(693, 438)
            if pixel_color != (0,153, 0):
                click(693, 438)

            #select coffre
            click(559, 587)

            time.sleep(0.5)

            size = 200
            box = (positionstartx-size/2, positionstarty-size/2, size, size)
            target_color = (47, 109, 171)
            found = search_and_click(box, target_color)
            #spawn Coffre Couleur: (47, 109, 171)

            time.sleep(0.3)

            #select sac
            click(537, 585)
            size = 200
            box = (positionstartx-size/2, positionstarty-size/2, size, size)
            target_color = (51, 113, 174)
            found = search_and_click(box, target_color)
            target_color = (47, 109, 171)
            found = search_and_click(box, target_color)
            #spawn sac Couleur: (47, 109, 171)


            time.sleep(2)
            passe_tour()
            return

        attackposx, attackposy = 650, 555
        nombre_coup = 3

        for i in range(1, nombre_coup+1):
            #selection attack
            click(attackposx, attackposy)
            time.sleep(1)

            box = (656, 463, 80, 55)
            # Couleur cible : bleu pur
            target_color = (0, 0, 255)
            found = search_and_click(box, target_color)
            if found:
                print("✅ Action effectuée.")
            else:
                box = (20, 75, 740-20, 475-75)
                search_and_click(box, target_color)

            if i==1:
                #verif distance
                pixel_color = get_pixel(599, 334)
                time.sleep(0.3)
                if pixel_color == (201,191,157):
                    click(722, 273)
                    #approche
                    #trouve enemie
                    box = (656, 463, 80, 55)
                    # Couleur cible : bleu pur

                    click(744, 468)
                    target_color = (0, 0, 255)
                    found = search(box, target_color)
                    box = (7, 58, 745-7, 485-58)
                    target_color = (0, 0, 255)
                    Tposx, Tposy = search(box, target_color)


                    #move_pathfind(positionstartx, positionstarty)


                    move_towards((positionstartx, positionstarty), (Tposx, Tposy))
                    click(744, 468)
                    time.sleep(1)
                    #selection attack
                    click(attackposx, attackposy)
                    time.sleep(0.4)
                    box = (656, 463, 80, 55)
                    # Couleur cible : bleu pur
                    target_color = (0, 0, 255)
                    found = search_and_click(box, target_color)

                    #reverif dist
                    pixel_color = get_pixel(599, 334)
                    if pixel_color == (201,191,157):
                        click(722, 273)

                    time.sleep(0.5)
            else:
                #verif distance
                pixel_color = get_pixel(599, 334)
                time.sleep(0.3)
                if pixel_color == (201,191,157):
                    click(722, 273)
                    passe_tour()
                    return




        time.sleep(1.5)

        #verif fin
        box = (570, 380, 10, 90)
        target_color = (255, 97, 0)
        found = search_and_click(box, target_color)
        if found:
            print("✅ Action effectuée.")
            etat = "fin_de_combat"
            return
        os.system("xdotool mousemove 342 262")

        time.sleep(2)
        passe_tour()

    time.sleep(0.8)


    #verif fin
    box = (570, 380, 10, 90)
    target_color = (255, 97, 0)
    found = search_and_click(box, target_color)
    if found:
        print("✅ Action effectuée.")
        etat = "fin_de_combat"
        return



def fin_de_combat():
    global etat
    print("Fin du combat...")
    send_telegram("⚔️ fin du combat !")
    click(554, 509)
    time.sleep(0.8)
    click(645, 145)
    time.sleep(0.7)
    os.system("xdotool mousemove 600 224 click --repeat 2 --delay 100 1")
    time.sleep(0.8)
    click(722, 91)



    etat = "collect"


def lvl_up():
    global etat
    print("Level up détecté !")
    
    send_telegram("lvl_up !")

    click(400, 298)

    etat = "collect"

def retour_banque():
    global etat
    global maps
    timemap = 11
    
    nb_map = len(mapsposition)

    nb_clicks = ((nb_map+1) - maps) % nb_map

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
    etat="recherche_pnj"

def recherche_pnj():
    global etat

    print("Recherche du pnj...")
    #search pnj
    box = (401, 167, 260, 200)
    target_color = (182, 147, 31)
    found = search_and_click(box, target_color)
    print(found)
    time.sleep(0.3)
    if found:
        pointer = root.query_pointer()
        x, y = pointer.root_x, pointer.root_y
        os.system(f"xdotool mousemove {x+20} {y+20} click 1")
        time.sleep(0.8)
        click(137, 303)
        time.sleep(2)
        click(609, 178)


        time.sleep(2)

        box = (543, 132, 738, 483)  # x, y, w, h
        filename = capture_region_bmp(box)
        print("✅ Capture BMP enregistrée :", filename)
        resp = send_photo_telegram(filename, "📸 Capture brute avec Xlib")
        print("📨 Réponse Telegram :", resp)
        
        ctrl_double_click_until_color(
            570, 234,
            check_x=570, check_y=234,
            target_color=(190, 185, 152),
            delay=1.2
        )

        time.sleep(0.5)
        click(722, 152)

        etat = "retour_peche"
        return



def retour_peche():
    global etat
    global maps
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
    maps = 1

    etat = "collect"

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
    global etat
    print("🔎 Bot démarré. Ctrl+C pour quitter.")

    while True:
        try:

            pos, color = get_mouse_pixel()
            x, y = pos
            print(f"État: {etat} | Position: {x},{y} | Couleur: {color}", end="\r")

            # Appel de la fonction correspondant à l'état
            if etat in actions:
                actions[etat]()  # exécutera la fonction associée

            # Ici tu pourras ajouter la logique pour passer d'un état à un autre
            # Exemple simple :
            # if etat == "collect" and condition:
            #     etat = "start_combat"

            time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n🔴 Bot arrêté.")
            break

if __name__ == "__main__":
    main()


