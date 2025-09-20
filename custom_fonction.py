#!/usr/bin/env python3
from Xlib import display, X
import os
import time
import random
import requests
import math
import struct
import variable

folder = "./telegram"
print("DEBUG: contenu du dossier :", os.listdir(folder))
# récupère le premier fichier du dossier
filename = os.listdir(folder)[0]
CHAT_ID = os.path.splitext(filename)[0]
filepath = os.path.join(folder, filename)
with open(filepath, "r") as f:
    TOKEN = f.read().strip()

URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"



# Initialisation X11
dsp = display.Display()
root = dsp.screen().root

def send_telegram(msg):
    requests.post(URL, data={"chat_id": CHAT_ID, "text": msg})



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

def search_color(x, y, target_color):
    """
    Scanne une boîte rectangulaire et clique sur le premier pixel trouvé
    avec la couleur cible.

    box = (x1, y1, width, height)
    target_color = (R, G, B)
    """
    
    w = 20
    h = w

    x1 = int(x-(w/2))
    y1 = int(y-(h/2))

    raw = root.get_image(x1, y1, w, h, X.ZPixmap, 0xffffffff)

    # Les données brutes sont sous forme BGRX pour chaque pixel
    data = raw.data
    stride = w * 4  # chaque pixel = 4 octets

    for row in range(h):
        for col in range(w):
            i = row * stride + col * 4
            b, g, r, _ = data[i:i+4]
            if (r, g, b) != target_color:
                return False  # trouvé une couleur différente
    return True


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

        pixel = search_color(x, y, target_color)
        print(f"🎨 Vérif pixel ({check_x},{check_y}) = {pixel}, attendu {target_color}")
  

        if pixel:
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
                click_notransition(px, py)
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
    os.system("xdotool keydown e") 

    for i in range(steps):
        nx = int(x1 + dx * i)
        ny = int(y1 + dy * i)
        os.system(f"xdotool mousemove {nx} {ny}")
        time.sleep(delay)
    os.system(f"xdotool mousemove {x2} {y2} click 1")
    os.system("xdotool keyup e") 

    time.sleep(0.15)

def click_notransition(x2, y2):
    """
    Déplace la souris progressivement de (x1,y1) vers (x2,y2)
    - steps = nombre d'étapes
    - delay = temps entre chaque petit mouvement
    """

    pointer = root.query_pointer()
    x1, y1 = pointer.root_x, pointer.root_y
    os.system(f"xdotool mousemove {x2} {y2} click 1")
    time.sleep(0.15)


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
    click(x, y)
    variable.positionstartx, variable.positionstarty = x, y
    time.sleep(0.3)
    return True


def start_combat():
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
    variable.positionstartx, variable.positionstarty = search(box, target_color)
    pixel_color = get_pixel(634, 314)
    time.sleep(0.3)
    click(variable.positionstartx, variable.positionstarty)

    time.sleep(0.5)

    click(720, 460)
    time.sleep(0.3)
    os.system("xdotool mousemove 342 262")
    time.sleep(1)
    variable.etat = "en_combat"
    variable.first_tour = True
    send_telegram("⚔️ Début combat !")
    return

def passe_tour():
    os.system("xdotool key F1")
    time.sleep(1)

def en_combat():
    print("Combat en cours...")

    #verif fin
    box = (570, 380, 10, 90)
    target_color = (255, 97, 0)
    found = search_and_click(box, target_color)
    if found:
        print("✅ Action effectuée.")
        variable.etat = "fin_de_combat"
        return



    #verif tour
    pixel_color = get_pixel(441, 515)
    time.sleep(0.3)

    if pixel_color == (255,102,0):
        #tour en cours

        if variable.first_tour:
            variable.first_tour = False

            #mode tactic
            pixel_color = get_pixel(693, 438)
            if pixel_color != (0,153, 0):
                click(693, 438)

            #select coffre
            click(559, 587)

            time.sleep(0.5)

            size = 200
            box = (variable.positionstartx-size/2, variable.positionstarty-size/2, size, size)
            target_color = (47, 109, 171)
            found = search_and_click(box, target_color)
            #spawn Coffre Couleur: (47, 109, 171)

            time.sleep(0.3)

            #select sac
            click(537, 585)
            size = 200
            box = (variable.positionstartx-size/2, variable.positionstarty-size/2, size, size)
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

                    move_towards((variable.positionstartx, variable.positionstarty), (Tposx, Tposy))
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
            variable.etat = "fin_de_combat"
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
        variable.etat = "fin_de_combat"
        return



def fin_de_combat():
    print("Fin du combat...")
    send_telegram("⚔️ fin du combat !")
    click(554, 509)
    time.sleep(0.8)
    click(645, 145)
    time.sleep(0.7)
    os.system("xdotool mousemove 600 224 click --repeat 2 --delay 100 1")
    time.sleep(0.8)
    click(722, 91)



    variable.etat = "collect"


def lvl_up():
    print("Level up détecté !")
    
    send_telegram("lvl_up !")

    click(400, 298)

    variable.etat = "collect"


def recherche_pnj():

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

        variable.etat = "retour_peche"
        return



