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


def generar_datos_estacion():
    # Genera la temperatura con media 55, varianza de 25, y dos decimales
    temperatura = round(random.gauss(55, 5), 2)
    temperatura = max(0, min(temperatura, 110))  # Limitar al rango [0, 110]

    # Genera la humedad con media 55 y varianza de 25, y como entero
    humedad = int(random.gauss(55, 5))
    humedad = max(0, min(humedad, 100))  # Limitar al rango [0, 100]

    # Genera la dirección del viento aleatoriamente
    direcciones_viento = ["N", "NO", "O", "SO", "S", "SE", "E", "NE"]
    direccion_viento = random.choice(direcciones_viento)

    # Crear el JSON con los datos generados
    datos = {
        "temperatura": temperatura,
        "humedad": humedad,
        "direccion_viento": direccion_viento
    }

    return json.dumps(datos)



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
        producer.produce(topic, value=datos, callback=acked)
        producer.flush()

        # Espera entre 15 y 30 segundos
        time.sleep(random.randint(15, 30))

except KeyboardInterrupt:
    print("Interrumpido por el usuario")
finally:
    producer.flush()
