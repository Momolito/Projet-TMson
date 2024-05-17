from tkinter import *
from tkinter import filedialog
import pygame
import numpy as np
import wave
import sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation

plt.style.use("bmh") #atyle de graphique
print("Veuillez sélectionner le fichier audio .wav que vous voulez analyser")#Importation de fichier wav à analyser
fichierAudio = filedialog.askopenfilename(initialdir="/Desktop/", title="Select a .wav file",filetypes=[("Sound file", "*.wav")])
f = float(input("Veuillez entrer la fréquence de votre son: ")) #l'utilisateur entre la fréquence
#Lecture du fichier audio
wav = wave.open(fichierAudio, "r")
raw = wav.readframes(-1) #trame en bytes
raw = np.frombuffer(raw, np.int16)
#Calcul
T=1/f #Période en (s)
E = wav.getframerate() #Fréquence d'échantillonage :nombre de points par seconde qui sont interprétés dans un fichier audio: double de l'audition humaine (généralement=44100)
dt=1/E #Varriation du temps entre les points du graphique du signal sonore



print(raw, len(raw))
time = np.linspace(0, len(raw) / (2*E), num=len(raw))
y=[0]*len(time)
saut=np.arange(0, len(raw),1)
#Partie Graphique
#Partie Graph
fig, graph= plt.subplots(figsize=(8,3))
graph.set(title="Graphique du son pour une periode",ylabel="Amplitude (Bytes) ", xlabel="Temps (s)") #titre et axe
fig.subplots_adjust(left=0.126, bottom=0.12, right=0.95, top=0.88, wspace=0.2, hspace=0.2) #parametre des dimensions de la fenêtre
line, = graph.plot(time, raw, color="c")  #graduation d'axe est couleur
graph.plot(time,y,linewidth=0.25, color="black",) #axe des x
graph.set_xlim(0,1/f) #limte des x (jusqu'à sa période)

def animate(i):
    line.set_ydata(raw[saut-len(raw)+i])  # update the data.
    return line,

ani = animation.FuncAnimation(
    fig, animate, interval=20, blit=True, save_count=50)
plt.show()


