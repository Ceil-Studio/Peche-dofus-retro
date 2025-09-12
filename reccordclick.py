#!/usr/bin/env python3
from Xlib import display, X

def main():
    dsp = display.Display()
    root = dsp.screen().root

    recorded_clicks = []

    # On "grab" tous les clics de la souris sur la root window
    for button in (1, 2, 3):  # gauche, milieu, droit
        root.grab_button(
            button=button,
            modifiers=X.AnyModifier,
            owner_events=True,
            event_mask=X.ButtonPressMask,
            pointer_mode=X.GrabModeAsync,
            keyboard_mode=X.GrabModeAsync,
            confine_to=X.NONE,
            cursor=X.NONE
        )

    print("🖱 Clique pour enregistrer une position. Ctrl+C pour quitter et sauvegarder.")

    try:
        while True:
            event = dsp.next_event()
            if event.type == X.ButtonPress:
                x, y = event.root_x, event.root_y
                recorded_clicks.append((x, y))
                print(f"✅ Clic enregistré: ({x}, {y})")
    except KeyboardInterrupt:
        print("\n💾 Sauvegarde des clics...")

        with open("clics.txt", "w") as f:
            for pos in recorded_clicks:
                f.write(f"({pos[0]}, {pos[1]}),\n")

        print(f"📂 Fichier 'clics.txt' créé avec {len(recorded_clicks)} positions.")

if __name__ == "__main__":
    main()
