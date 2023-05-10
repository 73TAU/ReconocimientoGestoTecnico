from SINCO.arduino import ArduinoGiroscopio
import numpy as np
import pandas as pd
import serial
import time

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import keyboard

fig = plt.figure()
ax = Axes3D(fig)

ar = ArduinoGiroscopio("COM8", 115200)
dt = pd.DataFrame(columns=['x', 'y', 'z'])
print(dt)

fin = 0

folder = "datos/"

while True:
    cad = ar.getDatos()
    print(cad)
    print(ar.giroscopio())
    x = int(ar.giroscopio()[0])
    y = int(ar.giroscopio()[1])
    z = int(ar.giroscopio()[2])


    dt = dt.append({'x': x, 'y': y, 'z': z}, ignore_index=True)
    if keyboard.is_pressed('q'):
        dt.to_csv(f'{folder}/datos_{time.time()}.csv')
        break
    print(fin)
    fin += 1

ax.plot(dt['x'], dt['y'], dt['z'])
plt.show()

# df.to_csv("df_personas.csv")
# df.to_html("df_personas.html")
# df.to_json("df_personas.json")

# df2 = pd.read_csv("df_personas.csv", index_col=0)


print(dt)

