"""
Costanti Globali & Configurazioni di Base per WeakAuras Suite — Warrior Fury 3.3.5a
===================================================================================
Contiene le condizioni di caricamento per Guerriero Furia 3.3.5a (WotLK 12340)
e le impostazioni grafiche condivise (font, texture, colori).
"""

# Condizioni di Caricamento (Load Conditions):
# Classe Guerriero (Class: WARRIOR) e talento Titan's Grip / Bloodsurge (Talent ID: 84 - Ramo Furia)
FURY_WARRIOR_LOAD = {
    "use_class": True,
    "class": {"single": "WARRIOR", "multi": {"WARRIOR": True}},
    "use_talent": True,
    "talent": {"single": 84, "multi": {84: True}},
    "use_vehicle": False,
}

# Tipografia e Texture Standard
FONT_EXPRESSWAY = "Expressway"
TEXTURE_STATUSBAR = "Interface\\TargetingFrame\\UI-StatusBar"
TEXTURE_WHITE8X8 = "Interface\\Buttons\\WHITE8X8"

# Palette Colori RGBA
COLOR_RAGE = [0.78, 0.12, 0.12, 1.0]          # Crimson intenso base
COLOR_RAGE_DUMP = [1.0, 0.65, 0.10, 1.0]     # Oro/Ambra per soglia scarico sicuro (>= 45)
COLOR_RAGE_STARVED = [0.45, 0.05, 0.05, 1.0]  # Rosso scuro (< 25)
COLOR_RAGE_BG = [0.10, 0.04, 0.04, 0.85]     # Sfondo scuro barra rabbia
COLOR_GOLD_BLOODSURGE = [1.0, 0.84, 0.0, 1.0] # Oro per proc Bloodsurge e glow
COLOR_CASTBAR = [0.0, 0.77, 1.0, 1.0]         # Azzurro classico castbar
COLOR_CASTBAR_BG = [0.05, 0.08, 0.12, 0.8]   # Sfondo castbar

