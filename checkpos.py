#!/usr/bin/env python3
from Xlib import display, X
import time
def get_mouse_data():
    dsp = display.Display()
    root = dsp.screen().root
    # Récupère la position de la souris
    pointer = root.query_pointer()
    x, y = pointer.root_x, pointer.root_y
    # Lit 1 pixel à cette position
    raw = root.get_image(x, y, 1, 1, X.ZPixmap, 0xffffffff)
    pixel = raw.data
    b, g, r, _ = pixel  # format BGRX
    return x, y, (r, g, b)
def main():
    print("🔎 Déplace ta souris, Ctrl+C pour quitter.")
    while True:
        try:
            x, y, color = get_mouse_data()
            print(f"🖱 Position: ({x}, {y}) | 🎨 Couleur: {color}", end="\r")
            time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n✅  Fin du script.")
            break
if __name__ == "__main__":
    main()
