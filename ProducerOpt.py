import time
import json
import random
from dotenv import load_dotenv
import os
from confluent_kafka import Producer

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración del Producer
bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')

kafka_config = {
    'bootstrap.servers': bootstrap_servers
}
producer = Producer(kafka_config)
topic = os.getenv('KAFKA_TOPIC')

# Mapear direcciones a valores de 3 bits
direccion_map = {
    "N": 0b000, "NO": 0b001, "O": 0b010, "SO": 0b011,
    "S": 0b100, "SE": 0b101, "E": 0b110, "NE": 0b111
}
direccion_reverse_map = {v: k for k, v in direccion_map.items()}


def generar_datos_estacion():
    # Genera la temperatura con media 55, varianza de 25, y un decimal
    temperatura = round(random.gauss(55, 5), 1)
    temperatura = max(0, min(int(temperatura * 10), 1100))  # Escalar y limitar a 11 bits

    # Genera la humedad con media 55 y varianza de 25, y como entero
    humedad = int(random.gauss(55, 5))
    humedad = max(0, min(humedad, 100))  # Limitar al rango [0, 100]

    # Genera la dirección del viento aleatoriamente
    direccion_viento = random.choice(list(direccion_map.keys()))

    return {"temperatura": temperatura, "humedad": humedad, "direccion_viento": direccion_viento}

def encode(data):
    """Codifica el JSON en un formato de 3 bytes."""
    temperatura = data["temperatura"]  # Ya en el rango [0, 1100] (11 bits)
    humedad = data["humedad"]  # Ya en el rango [0, 100] (7 bits)
    direccion_viento = direccion_map[data["direccion_viento"]]  # Mapear a 3 bits

    # Empaquetar los 3 valores en un entero de 24 bits
    payload = (temperatura << 13) | (humedad << 3) | direccion_viento

    # Convertir a bytes
    return payload.to_bytes(3, byteorder="big")


# Función de callback para confirmar el envío
def acked(err, msg):
    if err is not None:
        print(f"Falló al entregar el mensaje: {err}")
    else:
        print(f"Mensaje enviado a {msg.topic()} [{msg.partition()}]")

# Bucle de envío de datos
try:
    while True:
        datos = generar_datos_estacion()
        print(f"==>> datos:\n {datos}")
        
        # Codificar y enviar
        payload = encode(datos)
        print(f"==>> payload:\n {payload}")
        producer.produce(topic, value=payload, callback=acked)
        producer.flush()

        time.sleep(15)

except KeyboardInterrupt:
    print("Interrumpido por el usuario")
finally:
    producer.flush()
