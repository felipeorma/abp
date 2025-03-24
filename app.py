import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

# Configurar el campo vertical completo (StatsBomb 120x80, portería arriba)
pitch = VerticalPitch(pitch_type='statsbomb', half=False, pitch_color='#22312b', line_color='#c7d5cc')
fig, ax = pitch.draw(figsize=(6, 8))

# Etiquetas de zonas (coordenadas calculadas según límites de StatsBomb: área grande, mitad de campo, etc.)
zone_labels = {
    1:  (111, 9),   # zona 1: extremo izquierdo cerca de portería (x entre 102-120, y entre 0-18)
    2:  (111, 71),  # zona 2: extremo derecho cerca de portería (x 102-120, y 62-80)
    3:  (93, 9),    # zona 3: banda izquierda fuera del área (x 84-102, y 0-18)
    4:  (93, 71),   # zona 4: banda derecha fuera del área (x 84-102, y 62-80)
    14: (93, 29),   # zona 14: frontal izquierdo del área (x 84-102, y 18-40)
    15: (93, 51),   # zona 15: frontal derecho del área (x 84-102, y 40-62)
    12: (105, 15),  # zona 12: interior del área izquierda-baja (x 102-108, y 0-30)
    13: (105, 65),  # zona 13: interior del área derecha-baja (x 102-108, y 50-80)
    10: (114, 15),  # zona 10: interior del área izquierda-alta (x 108-120, y 0-30)
    11: (114, 65),  # zona 11: interior del área derecha-alta (x 108-120, y 50-80)
    5:  (114,  thirty),  # zona 5: zona cercana al poste izquierdo (x 108-120, aprox y 30)
    6:  (114,  fifty),   # zona 6: zona cercana al poste derecho (x 108-120, aprox y 50)
    7:  (114, 40),   # zona 7: centro de la portería (x 108-120, y 30-50, frente al arco)
    8:  (111, 18),   # zona 8: área izquierda junto al arco (cerca esquina del área chica izquierda)
    9:  (111, 62),   # zona 9: área derecha junto al arco (cerca esquina del área chica derecha)
    16: (72, 20),   # zona 16: mitad izquierda del campo (x 60-84, y 0-40)
    17: (72, 60)    # zona 17: mitad derecha del campo (x 60-84, y 40-80)
}
# Nota: 'thirty' y 'fifty' arriba representan aproximadamente 30 y 50 (coordenadas y), ajustar según necesidad.

# Dibujar cada número de zona en el campo
for zone, (x_coord, y_coord) in zone_labels.items():
    pitch.annotate(str(zone), (x_coord, y_coord), ax=ax, va='center', ha='center',
                   fontsize=12, color='red', weight='bold')

# Datos ficticios de la acción: zona de saque 17, zona de remate 4
origin_zone = 17
target_zone = 4

# Coordenadas representativas para las zonas 17 (origen) y 4 (remate)
origin_point = (72, 60)  # centro de zona 17
target_point = (93, 71)  # centro de zona 4

# Marcar el punto de la acción (remate) con scatter
pitch.scatter(target_point[0], target_point[1], ax=ax, s=100, color='deepskyblue', edgecolors='black', zorder=3, label='Remate (Zona 4)')

# Generar puntos aleatorios dentro de la zona 4 para el kde (densidad)
np.random.seed(1)
zone4_x = np.random.uniform(84, 102, size=50)  # x entre líneas de zona 4 (84 a 102)
zone4_y = np.random.uniform(62, 80, size=50)   # y entre líneas de zona 4 (62 a 80)

# Graficar el heatmap de densidad para zona 4
pitch.kdeplot(zone4_x, zone4_y, ax=ax, cmap='Reds', shade=True, levels=100, alpha=0.6)

# Opcional: marcar también el punto de origen de la jugada (zona 17) para referencia
pitch.scatter(origin_point[0], origin_point[1], ax=ax, s=80, color='yellow', edgecolors='black', zorder=3, label='Saque (Zona 17)')

# Título y leyenda
ax.set_title("Visualización de balón parado: Saque zona 17 -> Remate zona 4", fontsize=14, color='white')
ax.legend(loc='upper left', fontsize=10)

plt.show()
