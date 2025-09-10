#!/usr/bin/env python3
from pynput import mouse
import time
from Xlib import display, X

def get_mouse_position():
    dsp = display.Display()
    root = dsp.screen().root
    pointer = root.query_pointer()
    return pointer.root_x, pointer.root_y

def on_click(x, y, button, pressed):
    if pressed:  # uniquement au moment du clic
        coords = f"({x}, {y}),\n"
        if button != mouse.Button.left:
            return

        print(f"\n🖱 Clic {button} à {coords.strip()}")

        # Sauvegarde dans click.txt
        with open("click.txt", "a") as f:
            f.write(coords)

def main():
    print("🔎 Déplace ta souris (clic = sauvegardé dans click.txt, Ctrl+C pour quitter).")

    listener = mouse.Listener(on_click=on_click)
    listener.start()

    try:
        while True:
            x, y = get_mouse_position()
            print(f"🖱 Position: ({x}, {y})", end="\r")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n✅  Fin du script.")
        listener.stop()

if __name__ == "__main__":
    main()

