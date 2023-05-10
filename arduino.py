import serial
import time

# This class is used to read the data from the Arduino and store it in a list
# The ArduinoGiroscopio class reads data from an Arduino connected to a port and returns the values of
# the gyroscope and accelerometer.
class ArduinoGiroscopio:
    def __init__(self, Pcom, vau):
        """
        The function __init__() is a constructor that initializes the class

        :param Pcom: The port that the Arduino is connected to
        :param vau: baud rate
        """
        self.serialArduino = serial.Serial(Pcom, vau)
        time.sleep(1)

    def getDatos(self):
        """
        It reads a line from the serial port and decodes it from ascii to a string
        :return: The data from the serial port.
        """
        cad = self.serialArduino.readline().decode("ascii")
        return cad

    def giroscopio(self):
        """
        It takes a string of data from the accelerometer and splits it into three parts, then returns the three parts as a
        tuple
        :return: the values of the gyroscope.
        """
        finished = True
        while True:
            if finished != False:
                cad = self.getDatos()
                partg = cad.split(' ')
                if not len(partg) < 7:
                    gx, gy, gz = float(partg[2]), float(partg[0]), float(partg[1])
                    return gx, gy, gz
                else:
                    self.giroscopio()
            else:
                finished = False

    def acelerometro(self):
        """
        It takes a string, splits it into a list, and returns the 3rd, 4th, and 5th elements of that list
        :return: the x, y, and z values of the accelerometer.
        """
        finished = True
        while True:
            if finished != False:
                cad = self.getDatos()
                parta = cad.split(' ')
                if not len(parta) < 7:
                    ax, ay, az = float(parta[3]), float(parta[4]), float(parta[5])
                    return ax, ay, az
                else:
                    self.giroscopio()
            else:
                finished = False

    def valorAceleometroX(self):
        """
        This function returns the maximum value of the first element of a list of accelerometer
        readings.
        :return: the maximum value of the first component of the acceleration vector obtained from the
        acelerometro method, after taking 4 readings and storing them in a list.
        """
        x = 0
        a_acum = []
        while True:
            a = self.acelerometro()
            if x != 4:
                a_acum.append(a[0])
                x += 1
            else:
                break
        A = max(a_acum)
        return A

    def valorGiroscopioX(self):
        """
        This function returns the maximum value of the first four readings of the X-axis of a gyroscope.
        :return: the maximum value of the first element of the list `g_acum`, which is a list of the
        first four readings of the gyroscope.
        """
        x = 0
        g_acum = []
        while True:
            g = self.giroscopio()
            if x != 4:
                g_acum.append(g[0])
                x += 1
            else:
                break
        G = max(g_acum)
        return G
    


# This is a Python class that configures and reads data from an Arduino connected to an MPU6050
# sensor.
class Arduino_Lectura_Datos():

    def __init__(self):
        # Configuración del puerto serie
        self.arduino_port = '/dev/ttyUSB7'  # Cambia esto según el puerto COM de tu Arduino
        self.baud_rate = 115200
        self.ser = serial.Serial(self.arduino_port, self.baud_rate, timeout=1)

    # Esperar a que Arduino se reinicie
    time.sleep(2)

    # Función para enviar comandos a Arduino
    def enviar_comando(self, comando):
        
        self.ser.write(comando.encode())
        time.sleep(0.1)

    # Función para leer datos de Arduino
    def leer_datos(self):
        self.ser.write(b'd')
        line = self.ser.readline().decode().rstrip()
        return line

    # Configurar Arduino y MPU6050
    enviar_comando('s')
    time.sleep(2)
# Cerrar puerto serie
    def close(self):
        self.ser.close()

    while True:
        try:
            datos = leer_datos()
            print(datos)
        except KeyboardInterrupt:
            break
    
    close()