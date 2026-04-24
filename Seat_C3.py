import network
import time
from machine import Pin, ADC
import urequests
import json

#/home/jlgunner/Downloads/ESP32_GENERIC_C3-20260406-v1.28.0.bin

#Variables Globales
FASTAPI_URL = "http://192.168.0.5:8000/api/pressure"

# FUNCIÓN PARA ESTABLECER LA CONEXIÓN WIFI (STATION)

def connect(SSID, PASSWORD):
    import network                            # importa el módulo network
    global sta_if
    sta_if = network.WLAN(network.STA_IF)     # instancia el objeto -sta_if- para controlar la interfaz STA
    if not sta_if.isconnected():              # si no existe conexión...
        sta_if.active(True)                       # activa el interfaz STA del ESP32
        sta_if.connect(SSID, PASSWORD)            # inicia la conexión con el AP
        print('Conectando a la red', SSID +"...")
        while not sta_if.isconnected():           # ...si no se ha establecido la conexión...
            pass                                  # ...repite el bucle...
    print('Configuración de red (IP/netmask/gw/DNS):', sta_if.ifconfig())
    

def send_data(params):
    payload = {
        "deviceID": "S2",
        "Parametros": params
        }
    
    headers = {"Content-Type": "application/json"}
    try:
        response = urequests.post(FASTAPI_URL, data=json.dumps(payload), headers=headers)
        print(f"Respuesta: {response.status_code}")
        response.close()
        return True
    except Exception as e:
        print(f"Error al enviar datos: {e}")
        return False
    


# CONFIGURACIÓN DEL SENSOR 
seat_sensor1 = ADC(Pin(3))
seat_sensor1.atten(ADC.ATTN_11DB)

# INICIALIZACIÓN 
connect("Batcave", "Th3_0r@cl3")  


while True:
    lectura = seat_sensor1.read()
    
    if lectura < 1200:
        estado = "V"
    elif lectura < 1500:
        estado = "L"
    else:
        estado = "O"
        
    print(f"{estado} (Valor: {lectura})")
    
    if sta_if.isconnected():
        send_data(estado)
    else:
        print("Sin conexión WiFi...")
    
    time.sleep(0.5)




