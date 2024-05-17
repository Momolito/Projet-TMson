import math
import random
from tkinter import *
from tkinter import filedialog
import numpy as np
import wave
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import time
import sys
from PIL import Image, ImageTk
import pygame
from scipy import signal


class CreationAudio:
    def __init__(self):
        self.E = None
        self.ff = None
        self.t = None
        self.choixFO = None
        self.choixEq = None
        self.fbt = None

    def get_E(self):
        return self.E

    def get_ff(self):
        return self.ff

    def get_t(self):
        return self.t

    def get_choixFO(self):
        return self.choixFO

    def get_choixEq(self):
        return self.choixEq

    def get_fbt(self):
        return self.fbt

    def set_E(self):
        self.E = int(E_input.get())

    def set_ff(self):
        self.ff = float(frequenceF_input.get("1.0", 'end-1c'))

    def set_t(self):
        self.t = int(t_input.get("1.0", 'end-1c'))

    def set_choixFO(self, typee):
        self.choixFO = str(typee)

    def set_choixEq(self, num):
        self.choixEq = int(num)

    def set_fb(self):
        self.fbt = float(frequenceB_input.get("1.0", 'end-1c'))


def ConctructionSon(f, E, t):
    # PARAMÈTRES DU FICHIER WAVE À CRÉER

    # fréquence F d'échantillonage en Hz (valeur par défaut 44100 Hz)
    frequence = E
    # nb de canaux: 1 (mono) ou 2 (stéréo)
    canaux = 1
    # format d'échantillonnage - nb de bits par échantillon
    formt = 16
    # durée s
    duree = t

    # CRÉATION DU FICHIER

    monfichier = open("son.wav", "wb")  # écrire un fichier binaire

    # Attention, si un fichier du même nom existe dans le répertoire, il sera écrasé

    # PROCÉDURES DE CONVERSION ET D'ÉCRITURE DANS UN FICHIERBINAIRE

    def ecriretexte(texte, fichier):
        # prodédure qui convertit un texte caractère par caractère en octet et l'écrit dans le fichier
        # admet pour arguments un string et un fichier binaire
        for i in texte:  # pour chaque lettre du string,
            fichier.write(bytes([ord(i)]))  # on récupère sa correspondance décimale ASCII, on le convertit en octet
            # et on l'ajouter à la fin de fichier

    def ecrirenombre(n, entier, fichier):
        """
        convertir un entrier en n octets (lecture octet de poids fort à droite) - convention little endian
        et l'écrit dans le fichier
        admet pour arguments:
        - en entier n qui correspond au nb d'octets à écrire
        - un nombre entier compris entre 0 et 4 294 967 295 inclus si n = 4
                                           et 16 777 215 inclus si n = 3
                                           et 65 535 inclus si n = 2
                                           et 255 si inclus n = 1
        """
        for i in range(int(n)):  # pour chacun des n octets à coder
            fichier.write(bytes([(entier // (256 ** i)) % 256]))

    # ÉCRITURE DE L'EN-TÊTE (44 OCTETS)

    # octets de 1 à 4 (4 octets)
    ecriretexte("RIFF", monfichier)  # constante RIFF

    # octets de 5 à 8 (4 octets)
    # taille du fichier moins 8 octets (codée sur 4 octets)
    # ici 44 octets (en-tête) + format d'échantillon (en octets) x nbcanaux x nbd'échantillons (durée x F) - 8
    taille = int(44 + formt / 8 * canaux * duree * frequence - 8)
    ecrirenombre(4, taille, monfichier)

    # octets de 9 à 16 (8 octets)
    ecriretexte("WAVEfmt ", monfichier)  # constante formative

    # octets de 17 à 20 (4 octets)
    ecrirenombre(4, 16,
                 monfichier)  # format de l'en-tête du fichier.wav : les 16 octets suivants paramètrent le fichier

    # octets de 21 à 22 (2 octets
    ecrirenombre(2, 1, monfichier)  # pas de compression

    # octets de 23 à 24 (2 octets)
    ecrirenombre(2, canaux, monfichier)  # nb de canaux

    # octets de 25 à 28 (4 octets)
    ecrirenombre(4, frequence, monfichier)  # fréqeuence d'échantillonage

    # octets de 29 à 32 (4 octets)
    # débit en octets/s = format d'échantillonage en octets x nbcanaux x frequence
    debit = int(formt / 8 * canaux * frequence)
    ecrirenombre(4, debit, monfichier)  # débit en octets par seconde

    # octets de 33 à 34 (2 octets)
    ecrirenombre(2, int(formt / 8 * canaux),
                 monfichier)  # produit du format d'échantillonage (en octets) par le nb de canaux

    # octets de 35 à 36 (2 octets)
    ecrirenombre(2, formt, monfichier)  # format d'échantillonage - nb de bits par échantillon

    # DÉCLARATION DES DONNÉES

    # octets de 37 à 40 (4 octets)
    ecriretexte("data", monfichier)  # écrit data

    # octets 41 à 44 (4 octets)
    # taille du bloc de données = format d'échantillonage (en octet) x nbcanaux x duree (s) x fréquence
    taille = int(formt / 8 * canaux * duree * frequence)
    ecrirenombre(4, taille, monfichier)  # écrit le nb de fichiers du bloc de données

    # BLOC DE DONNÉES

    F = f  # au choix

    # 8 bits
    # format d'échantillonage 8 bits (données non signées)
    # la valeur maximale vaut la valeur maximale permise par le format d'échantillonage
    val_max = 2 ** formt  # c'est 2 puissance nb de bits
    # la sinusoïde va donc osciller entre 0 et val_max autour d'une valeur médiane ...
    val_med = val_max / 2
    # avec une amplitude qui vaudra aussi la valeur médiane donc de la forme
    #   valeur = val_med * (sin(2*pi*F*t)+1)

    # 16, 24, 32 bits
    # format d'échantillonage 16, 24 et 32 bits (données signées)
    # la valeur maximale vaut la valeur maximale permise par le format d'échantillonage
    # les données étant signées, la sinusoïde doit donc osciller entre - val_med + val_med
    # donc, elle est de la forme:
    #   valeur = val_med * sin(2*pi*F*t)

    # 8, 16, 24, 32 bits
    # la sinusoïde est de la forme:
    #   valeur = val_med * (sin(2*pi*F*t) + correction
    #   et correctoin à 0 pour les autres formats
    correction = 0
    if formt == 8:
        correction = 1

    # t est la date de l'échantillonage (en s)
    t = 0  # on initialise t à 0 s
    m = 0  # compteur1
    s = 0  # compteur2

    # valeur sera codée par n octets (n_octets est le format d'échantillonage en octets)
    n_octets = int(formt / 8)

    # on va compléter le dossier de façon itérative (pas par pas)
    # sous forme d'une boucle qui va s'effectuer en incrémentant t
    # jusqu'à ce qu'on atteigne la durée souhaitée
    # l'incrémentation Dt est la période de l'échantillonage
    # car l'inverse de la fréquence d'échantillonage
    Dt = 1 / frequence
    liste_valeur = []
    valeur = 0

    while t < duree:

        equations = [math.e ** (-t), math.sin(20 * t), math.sin(20 * t) * math.e ** (-t),
                     math.e ** (-t * math.sin(20 * t)), 1]

        if son.get_choixFO() == "sinus":

            valeur = int(equations[son.get_choixEq()] * (10000 * math.sin(2 * math.pi * 1 * F * t) + correction))

        elif son.get_choixFO() == "triangle":

            valeur = int(equations[son.get_choixEq()] * (
                    10000 * (8 / (math.pi ** 2)) * (((-1) ** 1) * (((2 * 1) - 1) ** (-2)) * (
                math.sin(2 * math.pi * ((2 * 1) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (((-1) ** 2) * (((2 * 2) - 1) ** (-2)) * (
                math.sin(2 * math.pi * ((2 * 2) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (((-1) ** 3) * (((2 * 3) - 1) ** (-2)) * (
                math.sin(2 * math.pi * ((2 * 3) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (((-1) ** 4) * (((2 * 4) - 1) ** (-2)) * (
                math.sin(2 * math.pi * ((2 * 4) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (((-1) ** 5) * (((2 * 5) - 1) ** (-2)) * (
                math.sin(2 * math.pi * ((2 * 5) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (((-1) ** 6) * (((2 * 6) - 1) ** (-2)) * (
                math.sin(2 * math.pi * ((2 * 6) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (((-1) ** 7) * (((2 * 7) - 1) ** (-2)) * (
                math.sin(2 * math.pi * ((2 * 7) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (((-1) ** 8) * (((2 * 8) - 1) ** (-2)) * (
                math.sin(2 * math.pi * ((2 * 8) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (((-1) ** 9) * (((2 * 9) - 1) ** (-2)) * (
                math.sin(2 * math.pi * ((2 * 9) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (
                            ((-1) ** 10) * (((2 * 10) - 1) ** (-2)) * (
                        math.sin(2 * math.pi * ((2 * 10) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (
                            ((-1) ** 11) * (((2 * 11) - 1) ** (-2)) * (
                        math.sin(2 * math.pi * ((2 * 11) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (
                            ((-1) ** 12) * (((2 * 12) - 1) ** (-2)) * (
                        math.sin(2 * math.pi * ((2 * 12) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (
                            ((-1) ** 13) * (((2 * 13) - 1) ** (-2)) * (
                        math.sin(2 * math.pi * ((2 * 13) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (
                            ((-1) ** 14) * (((2 * 14) - 1) ** (-2)) * (
                        math.sin(2 * math.pi * ((2 * 14) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (
                            ((-1) ** 15) * (((2 * 15) - 1) ** (-2)) * (
                        math.sin(2 * math.pi * ((2 * 15) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (
                            ((-1) ** 16) * (((2 * 16) - 1) ** (-2)) * (
                        math.sin(2 * math.pi * ((2 * 16) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (
                            ((-1) ** 17) * (((2 * 17) - 1) ** (-2)) * (
                        math.sin(2 * math.pi * ((2 * 17) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (
                            ((-1) ** 18) * (((2 * 18) - 1) ** (-2)) * (
                        math.sin(2 * math.pi * ((2 * 18) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (
                            ((-1) ** 19) * (((2 * 19) - 1) ** (-2)) * (
                        math.sin(2 * math.pi * ((2 * 19) - 1) * F * t))) +
                    10000 * (8 / (math.pi ** 2)) * (
                            ((-1) ** 20) * (((2 * 20) - 1) ** (-2)) * (
                        math.sin(2 * math.pi * ((2 * 20) - 1) * F * t))) + correction))

        elif son.get_choixFO() == "carrée":

            valeur = int(equations[son.get_choixEq()] * (10000 * (4 / math.pi) * ((((2 * 1) - 1) ** (-1)) * (
                math.sin(2 * math.pi * ((2 * 1) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 2) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 2) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 3) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 3) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 4) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 4) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 5) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 5) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 6) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 6) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 7) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 7) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 8) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 8) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 9) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 9) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 10) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 10) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 11) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 11) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 12) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 12) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 13) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 13) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 14) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 14) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 15) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 15) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 16) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 16) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 17) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 17) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 18) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 18) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 19) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 19) - 1) * F * t))) +
                                                         10000 * (4 / math.pi) * ((((2 * 20) - 1) ** (-1)) * (
                        math.sin(2 * math.pi * ((2 * 20) - 1) * F * t))) + correction))

        elif son.get_choixFO() == "dents":

            valeur = int(equations[son.get_choixEq()] * (10000 * (2 / math.pi) * (((-1) ** 1) * (1 ** (-1)) * (
                math.sin(2 * math.pi * 1 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 2) * (2 ** (-1)) * (
                        math.sin(2 * math.pi * 2 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 3) * (3 ** (-1)) * (
                        math.sin(2 * math.pi * 3 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 4) * (4 ** (-1)) * (
                        math.sin(2 * math.pi * 4 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 5) * (5 ** (-1)) * (
                        math.sin(2 * math.pi * 5 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 6) * (6 ** (-1)) * (
                        math.sin(2 * math.pi * 6 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 7) * (7 ** (-1)) * (
                        math.sin(2 * math.pi * 7 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 8) * (8 ** (-1)) * (
                        math.sin(2 * math.pi * 8 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 9) * (9 ** (-1)) * (
                        math.sin(2 * math.pi * 9 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 10) * (10 ** (-1)) * (
                        math.sin(2 * math.pi * 10 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 11) * (11 ** (-1)) * (
                        math.sin(2 * math.pi * 11 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 12) * (12 ** (-1)) * (
                        math.sin(2 * math.pi * 12 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 13) * (13 ** (-1)) * (
                        math.sin(2 * math.pi * 13 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 14) * (14 ** (-1)) * (
                        math.sin(2 * math.pi * 14 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 15) * (15 ** (-1)) * (
                        math.sin(2 * math.pi * 15 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 16) * (16 ** (-1)) * (
                        math.sin(2 * math.pi * 16 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 17) * (17 ** (-1)) * (
                        math.sin(2 * math.pi * 17 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 18) * (18 ** (-1)) * (
                        math.sin(2 * math.pi * 18 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 19) * (19 ** (-1)) * (
                        math.sin(2 * math.pi * 19 * F * t))) +
                                                         10000 * (2 / math.pi) * (((-1) ** 20) * (20 ** (-1)) * (
                        math.sin(2 * math.pi * 20 * F * t))) + correction))

        elif son.get_choixFO() == "battements":

            son.set_fb()

            valeur = int(equations[son.get_choixEq()] * (10000 * math.sin(2 * math.pi * F * t) + 10000 * math.sin(
                2 * math.pi * (F + son.get_fbt()) * t) + correction))

        liste_valeur.append(valeur)
        t = t + Dt  # à chaque boucle, on incrémente t de la période d'échantillonage
    max_value = None
    for num in liste_valeur:
        if max_value is None or abs(num) > max_value:
            max_value = num
    optimis = (val_med - 1) / max_value
    while m < duree:  # ***************************************Deuxième partie**************************************
        valeur2 = int(optimis * liste_valeur[s])
        for canal in range(canaux):  # pour chaque canal
            ecrirenombre(n_octets, valeur2, monfichier)
        m = m + Dt  # à chaque boucle, on incrémente t de la période d'échantillonage
        s = s + 1
    monfichier.close()  # on referme le fichier


def clear_btn_fonction():  # permet d'effacer les valeurs dans les cases input
    frequenceF_input.delete(1.0, "end"), t_input.delete(1.0, "end")
    frequenceF_input.insert(1.0, "0"), t_input.insert(1.0, "0")


def creation_btn_fonction():
    son.set_ff(), son.set_E(), son.set_t()
    ConctructionSon(son.get_ff(), son.get_E(), son.get_t())


def jouer_btn_fonction():
    sonfichier = pygame.mixer.Sound('son.wav')
    sonfichier.play(loops=0)


def return_btn_fonction():
    root.destroy()
    sys.stdout.flush()
    os.execl(sys.executable, 'python', __file__, *sys.argv[1:])


# Interface graphique
root = Tk()
root.iconbitmap("logo.ico")
root.title("Création d'un son à l'aide d'équations mathématiques")
# root.geometry("500x500")
# root.resizable(height=False, width=False)

pygame.mixer.init()

frame1 = Frame(root)
frame1.grid(columnspan=2, rowspan=4)
frame2 = Frame(root)
frame2.grid(columnspan=5, rowspan=3)
frame3 = Frame(root)
frame3.grid(columnspan=3, rowspan=1)
frame4 = Frame(root)
frame4.grid(columnspan=4, rowspan=3)
frame5 = Frame(root)
frame5.grid(columnspan=3, rowspan=1)

son = CreationAudio()

titre = Label(frame1, text="Création d'un son", font="Raleway 15 bold", height=1, width=20)
titre.grid(column=0, columnspan=2, row=0)

frequenceF_text = Label(frame1, text="Entrez la fréquence fondamentale de votre son:", anchor="e",
                        width=55)  # Label de la f.Fondamentale
frequenceF_text.grid(column=0, row=1)
frequenceF_input = Text(frame1, bg="white", height=1, width=8)
frequenceF_input.grid(column=1, row=1)

E_text = Label(frame1, text="Entrez la fréquence d'échantillonage désirée (par défault 44100 Hz):", anchor="e",
               width=55)  # Label de la f.Échantillonnage
E_text.grid(column=0, row=2)
E_valeurs = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000, 352800, 384000]
E_input = StringVar(frame1)
E_input.set(E_valeurs[5])
E_affichage = OptionMenu(frame1, E_input, *E_valeurs)
E_affichage.grid(column=1, row=2)

t_text = Label(frame1, text="Entrez la durée (en seconde) de votre son:", anchor="e", width=55)  # Label de la durée
t_text.grid(column=0, row=3)
t_input = Text(frame1, bg="white", height=1, width=8)
t_input.grid(column=1, row=3)

# Bouton clear
clear_text = StringVar()
clear_btn = Button(frame1, textvariable=clear_text, command=lambda: clear_btn_fonction(), bg="#0df1af", height=1,
                   width=15)
clear_text.set("Effacer")
clear_btn.grid(column=1, row=4)

frequenceF_input.insert(1.0, "440"), t_input.insert(1.0, "5")  # valeur de base 0

# Partie équations mathématiques

titre1 = Label(frame2, text="Équations mathématiques", font="Raleway 15 bold", height=1, width=20, padx=4, pady=3)
titre1.grid(column=1, columnspan=3, row=0)

# formes d'onde

formeOnde_label = Label(frame2, text="Formes d'onde:", anchor="e", width=12)
formeOnde_label.grid(column=0, row=1)
formeOnde_valeurs = ["Sinusoïde", "Triangulaire", "Carrée", "Dents de scie", "Battements"]
formeOnde_input = IntVar(root)

Radiobutton(frame2, text=formeOnde_valeurs[0], variable=formeOnde_input, value=1, command=lambda:
son.set_choixFO("sinus")).grid(column=1, row=1)
img = Image.open("sinewave.png")
img_resize = img.resize((53, 28), Image.ANTIALIAS)
new_img = ImageTk.PhotoImage(img_resize)
ImageSinus = Label(frame2, image=new_img)
ImageSinus.grid(column=1, row=2)

Radiobutton(frame2, text=formeOnde_valeurs[1], variable=formeOnde_input, value=2, command=lambda:
son.set_choixFO("triangle")).grid(column=2, row=1)
img3 = Image.open("trianglewave.png")
img_resize3 = img3.resize((53, 28), Image.ANTIALIAS)
new_img3 = ImageTk.PhotoImage(img_resize3)
ImageTriangle = Label(frame2, image=new_img3)
ImageTriangle.grid(column=2, row=2)

Radiobutton(frame2, text=formeOnde_valeurs[2], variable=formeOnde_input, value=3, command=lambda:
son.set_choixFO("carrée")).grid(column=3, row=1)
img2 = Image.open("squarewave.png")
img_resize2 = img2.resize((53, 28), Image.ANTIALIAS)
new_img2 = ImageTk.PhotoImage(img_resize2)
ImageSquare = Label(frame2, image=new_img2)
ImageSquare.grid(column=3, row=2)

Radiobutton(frame2, text=formeOnde_valeurs[3], variable=formeOnde_input, value=4, command=lambda:
son.set_choixFO("dents")).grid(column=4, row=1)
img4 = Image.open("sawtoothwave.png")
img_resize4 = img4.resize((53, 28), Image.ANTIALIAS)
new_img4 = ImageTk.PhotoImage(img_resize4)
ImageTriangle = Label(frame2, image=new_img4)
ImageTriangle.grid(column=4, row=2)

# Battement

Radiobutton(frame3, text=formeOnde_valeurs[4], variable=formeOnde_input, value=5, command=lambda:
son.set_choixFO("battements")).grid(column=0, row=0)

Battement_label = Label(frame3, text="Fréquence:", anchor=CENTER, width=12)
Battement_label.grid(column=1, row=0)

frequenceB_input = Text(frame3, bg="white", height=1, width=3)
frequenceB_input.grid(column=2, row=0)

# Attaques

Eqmath_label = Label(frame4, text="Attaques:", anchor="e", width=12)
Eqmath_label.grid(column=0, row=3)
Eqmath_valeurs = ["", "", "", "", "Aucun"]
Eqmath_input = IntVar(root)

Radiobutton(frame4, text=Eqmath_valeurs[0], variable=Eqmath_input, value=1, command=lambda:
son.set_choixEq(0)).grid(column=1, row=3)
img5 = Image.open("e-x.png")
img_resize5 = img5.resize((44, 32), Image.ANTIALIAS)
new_img5 = ImageTk.PhotoImage(img_resize5)
ImageEq1 = Label(frame4, image=new_img5)
ImageEq1.grid(column=1, row=4)

Radiobutton(frame4, text=Eqmath_valeurs[1], variable=Eqmath_input, value=2, command=lambda:
son.set_choixEq(1)).grid(column=2, row=3)
img6 = Image.open("sinx.png")
img_resize6 = img6.resize((57, 31), Image.ANTIALIAS)
new_img6 = ImageTk.PhotoImage(img_resize6)
ImageEq2 = Label(frame4, image=new_img6)
ImageEq2.grid(column=2, row=4)

Radiobutton(frame4, text=Eqmath_valeurs[2], variable=Eqmath_input, value=3, command=lambda:
son.set_choixEq(2)).grid(column=3, row=3)
img7 = Image.open("e-xsinx.png")
img_resize7 = img7.resize((86, 32), Image.ANTIALIAS)
new_img7 = ImageTk.PhotoImage(img_resize7)
ImageEq3 = Label(frame4, image=new_img7)
ImageEq3.grid(column=3, row=4)

Radiobutton(frame4, text=Eqmath_valeurs[3], variable=Eqmath_input, value=4, command=lambda:
son.set_choixEq(3)).grid(column=4, row=3)
img8 = Image.open("e-xsinx.png")
img_resize8 = img8.resize((75, 28), Image.ANTIALIAS)
new_img8 = ImageTk.PhotoImage(img_resize8)
ImageEq4 = Label(frame4, image=new_img8)
ImageEq4.grid(column=4, row=4)

Radiobutton(frame4, text=Eqmath_valeurs[4], variable=Eqmath_input, value=5, command=lambda:
son.set_choixEq(4)).grid(column=5, row=3)

# Bouton Créer
analyse_text = StringVar()
analyse_btn = Button(frame5, textvariable=analyse_text, command=lambda: creation_btn_fonction(), bg="#0df1af",
                     height=1, width=15)
analyse_text.set("Créer!")
analyse_btn.grid(column=1, row=6)

# Bouton Retour
return_text = StringVar()
return_btn = Button(frame5, textvariable=return_text, command=lambda: return_btn_fonction(), bg="gray", height=1,
                    width=15)
return_text.set("Retour")
return_btn.grid(column=0, row=6)

# Bouton Jouer le son
jouer_text = StringVar()
jouer_btn = Button(frame5, textvariable=jouer_text, command=lambda: jouer_btn_fonction(), bg="yellow", height=1,
                   width=15)
jouer_text.set("Jouer le son!")
jouer_btn.grid(column=2, row=6)

root.mainloop()