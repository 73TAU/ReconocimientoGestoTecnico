from PoseModule import PoseDetector

detector = PoseDetector()

def articulaciones(lmlist, img, extremidad, lado, angulos, numExtremidades):
    """
     extremidad: es la extremidades a unsar
     angulos: es el angulo de cada extremidad 
     numExtremidades: cantidad de extremidades a usar
    
     cada extremidad usada tiene un par de ennlas y apra referirce a una se usa lo siguiente
     Derecha = 1
     Izquierda = 2
     H = Hombro
     C = Cadera
     P = Pierna
     B = Brazo 
     ejemplo: si se va a usar el brazo izquierdo seria asi [B,2]
    """
    extremidades = {
        ('H', 1): ("14", "12", "24"),
        ('H', 2): ("13", "11", "23"),
        ('C', 1): ("23", "24", "26"),
        ('C', 2): ("24", "23", "25"),
        ('P', 1): ("24", "26", "28"),
        ('P', 2): ("23", "25", "27"),
        ('B', 1): ("12", "14", "16"),
        ('B', 2): ("11", "13", "15")
    }
    
    for i in range(numExtremidades):
        extremidad_actual = extremidad[i]
        lado_actual = lado[i]
        anguloa = detector.findAngle(lmlist, img, *extremidades[(extremidad_actual, lado_actual)], True)
        angulos[i] = anguloa
