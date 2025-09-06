#!/usr/bin/env python3
from Xlib import display, X
import os
import time
import random
import requests
import math
import struct

TOKEN = "7343462874:AAFxCdI5-8YKEdW11la4OIWnBt45ogB02hI"
CHAT_ID = "2118541386"
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

def send_telegram(msg):
    requests.post(URL, data={"chat_id": CHAT_ID, "text": msg})


send_telegram("🚀 Bot lancé sur le VPS !")

# Initialisation X11
dsp = display.Display()
root = dsp.screen().root

# Etat initial
etat = "retour_peche"
maps = 1
first_tour = True

def capture_region_bmp(box, filename="capture.bmp"):
    """
    Capture une région et sauvegarde en BMP (format brut).
    """
    x, y, w, h = box
    w, h = w-x, h-y
    raw = root.get_image(x, y, w, h, X.ZPixmap, 0xffffffff)

    # Pixels bruts BGRX
    data = raw.data

    # Chaque ligne doit être alignée sur 4 octets
    row_padded = (w * 3 + 3) & ~3
    filesize = 54 + row_padded * h

    # Header BMP (14 octets)
    bmp_header = struct.pack(
        '<2sIHHI',
        b'BM', filesize, 0, 0, 54
    )
    # DIB header (40 octets) -> hauteur signée (int)
    dib_header = struct.pack(
        '<IiiHHIIiiII',
        40, w, -h, 1, 24, 0, row_padded * h, 0, 0, 0, 0
    )

    # Convertir BGRX -> BGR (supprimer alpha)
    pixels = bytearray()
    for row in range(h):
        offset = row * w * 4
        line = bytearray()
        for col in range(w):
            b, g, r, _ = data[offset+col*4:offset+col*4+4]
            line.extend([b, g, r])
        # padding
        while len(line) < row_padded:
            line.append(0)
        pixels.extend(line)

    with open(filename, "wb") as f:
        f.write(bmp_header)
        f.write(dib_header)
        f.write(pixels)

    return filename

def send_photo_telegram(filename, caption=""):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    with open(filename, "rb") as f:
        files = {"photo": f}
        data = {"chat_id": CHAT_ID, "caption": caption}
        r = requests.post(url, files=files, data=data)
    return r.json()


def ctrl_double_click_until_color(x, y, check_x, check_y, target_color, delay=0.5):
    """
    Maintient Ctrl et double clique à (x,y) jusqu'à ce que le pixel (check_x,check_y)
    corresponde à target_color.

    - x, y : position du double-clic
    - check_x, check_y : pixel à vérifier après chaque clic
    - target_color : (R,G,B) attendu
    - delay : temps d’attente entre chaque tentative
    """
    while True:
        print(f"🖱️ Double clic Ctrl+({x},{y})...")
        os.system(f"xdotool keydown ctrl mousemove {x} {y} click --repeat 2 --delay 100 1 keyup ctrl")

        time.sleep(delay)  # petit délai pour que l’écran s’actualise

        pixel = get_pixel(check_x, check_y)
        print(f"🎨 Vérif pixel ({check_x},{check_y}) = {pixel}, attendu {target_color}")

        if pixel == target_color:
            print("✅ Couleur correcte détectée, on arrête la boucle.")
            break
        else:
            print("❌ Pas la bonne couleur, on recommence...")

def get_mouse_pixel():
    pointer = root.query_pointer()
    x, y = pointer.root_x, pointer.root_y
    raw = root.get_image(x, y, 1, 1, X.ZPixmap, 0xffffffff)
    b, g, r, _ = raw.data
    return (x, y), (r, g, b)

def get_pixel(x, y):
    x = max(0, x)
    y = max(0, y)
    raw = root.get_image(x, y, 1, 1, X.ZPixmap, 0xffffffff)
    b, g, r, _ = raw.data
    return (r, g, b)

def search_and_click(box, target_color):
    """
    Scanne une boîte rectangulaire et clique sur le premier pixel trouvé
    avec la couleur cible.

    box = (x1, y1, width, height)
    target_color = (R, G, B)
    """
    x1, y1, w, h = box
    x1 = int(max(0, x1))
    y1 = int(max(0, y1))

    raw = root.get_image(x1, y1, w, h, X.ZPixmap, 0xffffffff)

    # Les données brutes sont sous forme BGRX pour chaque pixel
    data = raw.data
    stride = w * 4  # chaque pixel = 4 octets

    for row in range(h):
        for col in range(w):
            i = row * stride + col * 4
            b, g, r, _ = data[i:i+4]
            if (r, g, b) == target_color:
                px = x1 + col
                py = y1 + row
                print(f"🎯 Pixel trouvé à ({px}, {py}), clic !")
                time.sleep(0.5)
                click(px, py)
                return True
    print("❌ Aucun pixel trouvé dans la zone.")
    return False

def search(box, target_color):
    """
    Scanne une boîte rectangulaire et clique sur le premier pixel trouvé
    avec la couleur cible.

    box = (x1, y1, width, height)
    target_color = (R, G, B)
    """
    x1, y1, w, h = box
    raw = root.get_image(x1, y1, w, h, X.ZPixmap, 0xffffffff)

    # Les données brutes sont sous forme BGRX pour chaque pixel
    data = raw.data
    stride = w * 4  # chaque pixel = 4 octets

    for row in range(h):
        for col in range(w):
            i = row * stride + col * 4
            b, g, r, _ = data[i:i+4]
            if (r, g, b) == target_color:
                px = x1 + col
                py = y1 + row
                time.sleep(0.5)
                os.system(f"xdotool mousemove {px} {py}")
                return px, py
    print("❌ Aucun pixel trouvé dans la zone.")
    return (700, 700)

def mousemove(x2, y2):
    """
    Déplace la souris progressivement de (x1,y1) vers (x2,y2)
    - steps = nombre d'étapes
    - delay = temps entre chaque petit mouvement
    """

    # pointer = root.query_pointer()
    # x1, y1 = pointer.root_x, pointer.root_y
    # steps=20
    # delay=0.02
    # dx = (x2 - x1) / steps
    # dy = (y2 - y1) / steps
    #
    # for i in range(steps):
    #     nx = int(x1 + dx * i)
    #     ny = int(y1 + dy * i)
    #     os.system(f"xdotool mousemove {nx} {ny}")
    #     time.sleep(delay)
    os.system(f"xdotool mousemove {x2} {y2}")
    time.sleep(0.03)

def click(x2, y2):
    """
    Déplace la souris progressivement de (x1,y1) vers (x2,y2)
    - steps = nombre d'étapes
    - delay = temps entre chaque petit mouvement
    """

    pointer = root.query_pointer()
    x1, y1 = pointer.root_x, pointer.root_y
    steps=15
    delay=0.01
    dx = (x2 - x1) / steps
    dy = (y2 - y1) / steps

    for i in range(steps):
        nx = int(x1 + dx * i)
        ny = int(y1 + dy * i)
        os.system(f"xdotool mousemove {nx} {ny}")
        time.sleep(delay)
    os.system(f"xdotool mousemove {x2} {y2} click 1")
    time.sleep(0.15)

def move_pathfind(x2, y2):
    """
    Déplace la souris progressivement de (x1,y1) vers (x2,y2)
    - steps = nombre d'étapes
    - delay = temps entre chaque petit mouvement
    """
    global positionstartx, positionstarty
    pointer = root.query_pointer()
    x1, y1 = pointer.root_x, pointer.root_y
    steps=30
    delay=0.1
    dx = (x2 - x1) / steps
    dy = (y2 - y1) / steps

    for i in range(steps):
        nx = int(x1 + dx * i)
        ny = int(y1 + dy * i)
        os.system(f"xdotool mousemove {nx} {ny}")
        pos, col = get_mouse_pixel()
        if col == (255, 102, 0):
            positionstartx, positionstarty = nx, ny
            os.system(f"xdotool click 1")
            return
        time.sleep(delay)

    time.sleep(0.3)



def move_towards(player_pos, enemy_pos, a=50*1.5, b=35*1.5, step=25):
    px, py = player_pos
    ex, ey = enemy_pos

    dx, dy = ex - px, ey - py
    angle = math.atan2(dy, dx)

    candidates = []

    # 1. tester la direction directe en priorité
    x = int(px + a * math.cos(angle))
    y = int(py + b * math.sin(angle))
    if is_clickable(x, y):
        return click_and_update(x, y)

    # 2. sinon, explorer autour de l’ellipse
    for delta in range(step, 181, step):
        for sign in [-1, 1]:
            new_angle = angle + sign * math.radians(delta)
            x = int(px + a * math.cos(new_angle))
            y = int(py + b * math.sin(new_angle))
            if is_clickable(x, y):
                # on garde aussi la distance à l’ennemi pour choisir le meilleur
                dist_enemy = (ex - x) ** 2 + (ey - y) ** 2
                candidates.append((dist_enemy, x, y))

    # 3. choisir la case valide qui rapproche le plus de l’ennemi
    if candidates:
        candidates.sort(key=lambda c: c[0])  # tri par distance à l’ennemi
        _, best_x, best_y = candidates[0]
        return click_and_update(best_x, best_y)

    return False


def is_clickable(x, y):
    """Retourne True si la case est orange cliquable"""
    mousemove(x, y)
    time.sleep(0.1)
    color = get_pixel(x, y)
    return color == (255, 102, 0)


def click_and_update(x, y):
    """Clique sur la case et met à jour la position globale"""
    global positionstartx, positionstarty
    click(x, y)
    positionstartx, positionstarty = x, y
    time.sleep(0.3)
    return True

mapsposition = [
    (615, 478),
    (31, 422),
    (137, 70),
    (722, 124),

]
resources_positions = {
    1: [
        (30, 230),
        (85, 236),
        (216, 249),
        (273, 252),
        (349, 286),
        (350, 317),
        (375, 358),
        (402, 398),
        (432, 411),
        (429, 457),
    ],
    2: [
        (428, 82),
        (429, 111),
        (482, 166),
        (509, 177),
        (511, 205),
        (483, 245),
        (429, 269),
        (403, 284),
        (373, 325),
        (349, 338),
        (269, 352),
        (217, 379),
        (167, 380),
        (137, 365),
        (81, 339),
    ],
    3: [
        # # ➕ ajoute positions pour map 3
        (668, 341),
        (530, 387),
        (372, 330),
        (295, 262),
        (241, 234),
        (270, 168),
        (295, 155),
        (324, 84),
    ],
    4: [
        # ➕ ajoute positions pour map 4
        # (349, 477),
        (350, 450),
        (324, 406),
        (270, 381),
        (270, 352),
        (270, 326),
        (296, 195),
        (322, 246),
        (484, 194),
        (612, 180),
        (643, 196),
        (675, 212),
    ]
}


def change_map():
    global maps

    time.sleep(4)

    x, y = mapsposition[maps-1]

    click(x, y)


    maps = maps+1

    if maps>4:
        maps = 1

    time.sleep(6)






def do_collect():
    global etat
    global maps
    print("Collecte en cours...")

    positions = resources_positions[maps][:]
    # random.shuffle(positions)  # mélange aléatoire

    #verif surpoid
    pixel_color = get_pixel(391, 519)
    if pixel_color == (255, 102, 0):
        etat="retour_banque"
        return

    #verif combat 
    pixel_color = get_pixel(720, 460)

    if pixel_color == (255, 102, 0):
        etat="start_combat"
        return

    for pos in positions:
        x, y = pos
        # Clique sur la ressource
        click(x, y)
        offset_x = x+50
        offset_y = y+21
        time.sleep(0.3)  # petit délai pour que l'action soit visible
        
        pixel_color = get_pixel(offset_x, offset_y)

        if pixel_color == (213, 207, 170):
            print(f"🎯 Couleur détectée à {offset_x},{offset_y} | clic effectué")
            click(offset_x, offset_y)
            time.sleep(16)

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

        #selection attack
        click(620, 556)
        time.sleep(1)

        box = (656, 463, 80, 55)
        # Couleur cible : bleu pur
        target_color = (0, 0, 255)
        found = search_and_click(box, target_color)
        if found:
            print("✅ Action effectuée.")

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
            box = (7, 58, 730, 400)
            target_color = (0, 0, 255)
            Tposx, Tposy = search(box, target_color)


            #move_pathfind(positionstartx, positionstarty)


            move_towards((positionstartx, positionstarty), (Tposx, Tposy))
            click(744, 468)
            time.sleep(1)
            #selection attack
            click(620, 556)
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




        time.sleep(1.5)

        #verif fin
        box = (570, 380, 10, 30)
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
    box = (570, 380, 10, 30)
    target_color = (255, 97, 0)
    found = search_and_click(box, target_color)
    if found:
        print("✅ Action effectuée.")
        etat = "fin_de_combat"
        return
    time.sleep(0.3)






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

    nb_clicks = (5 - maps) % 4

    if nb_clicks>0:
        for i in range(nb_clicks):
            change_map()


    print("Retour à la banque...")
    send_telegram("🏦 Le bot retourne à la banque.")
    time.sleep(2)
    click(723, 259)
    time.sleep(6)
    click(722, 341)
    time.sleep(6)
    click(506, 191)
    click(535, 203)
    click(161, 260)
    time.sleep(10)
    click(296, 475)
    time.sleep(6)
    click(407, 475)
    time.sleep(6)
    click(349, 477)
    time.sleep(6)
    click(401, 473)
    time.sleep(6)
    click(29, 288)
    time.sleep(6)
    click(30, 292)
    time.sleep(6)
    click(630, 180)
    time.sleep(6)

    etat="recherche_pnj"

def recherche_pnj():
    global etat

    print("Recherche du pnj...")
    #search pnj
    box = (401, 167, 260, 200)
    target_color = (182, 147, 31)
    found = search_and_click(box, target_color)
    time.sleep(0.3)
    pointer = root.query_pointer()
    x, y = pointer.root_x, pointer.root_y
    os.system(f"xdotool mousemove {x+20} {y+20} click 1")
    time.sleep(0.8)
    click(137, 303)
    time.sleep(2)
    click(609, 178)
    box = (543, 132, 738, 483)  # x, y, w, h
    filename = capture_region_bmp(box)
    print("✅ Capture BMP enregistrée :", filename)
    resp = send_photo_telegram(filename, "📸 Capture brute avec Xlib")
    print("📨 Réponse Telegram :", resp)

    time.sleep(2)

    ctrl_double_click_until_color(
        571, 234,
        check_x=565, check_y=233,
        target_color=(190, 185, 152),
        delay=0.5
    )

    time.sleep(0.5)
    click(722, 152)

    etat = "retour_peche"



def retour_peche():
    global etat
    global maps
    print("Retour à la pêche...")
    send_telegram("🎣 Le bot retourne à la pêche.")

    time.sleep(1)
    click(218, 409)
    time.sleep(6)
    click(32, 290)
    time.sleep(6)
    click(509, 269)
    click(565, 303)
    time.sleep(3)
    click(30, 449)
    time.sleep(6)
    click(30, 368)
    time.sleep(6)
    click(512, 474)
    time.sleep(6)
    click(639, 463)
    time.sleep(6)
    click(722, 476)
    time.sleep(6)
    click(723, 421)
    time.sleep(6)
    click(721, 312)
    time.sleep(6)
    click(721, 289)
    time.sleep(6)
    click(720, 398)
    time.sleep(6)
    click(723, 423)
    time.sleep(6)
    click(346, 475)
    time.sleep(2)

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

