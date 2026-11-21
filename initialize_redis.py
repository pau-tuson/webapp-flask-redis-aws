import os
import redis

# Fase 0: redis instalado en la misma EC2 -> localhost
# (en la fase 1 hay que cambiar esto por el endpoint de ElastiCache y poner ssl=True)
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))


def initialize_products(redis_client):
    # 10 productos de prueba para la tienda
    productos = [
        {"id": "1", "name": "Teclado mecanico", "price": 59.99, "description": "Teclado con switches rojos", "stock": 15},
        {"id": "2", "name": "Raton inalambrico", "price": 24.50, "description": "Raton bluetooth ergonomico", "stock": 30},
        {"id": "3", "name": "Monitor 24 pulgadas", "price": 149.00, "description": "Monitor Full HD IPS", "stock": 8},
        {"id": "4", "name": "Auriculares", "price": 39.90, "description": "Auriculares con microfono", "stock": 20},
        {"id": "5", "name": "Webcam HD", "price": 34.99, "description": "Webcam 1080p con microfono", "stock": 12},
        {"id": "6", "name": "Disco SSD 1TB", "price": 79.95, "description": "SSD NVMe M.2", "stock": 10},
        {"id": "7", "name": "Memoria USB 64GB", "price": 9.99, "description": "Pendrive USB 3.0", "stock": 50},
        {"id": "8", "name": "Alfombrilla", "price": 7.50, "description": "Alfombrilla de raton grande", "stock": 40},
        {"id": "9", "name": "Hub USB-C", "price": 29.00, "description": "Hub con 4 puertos USB y HDMI", "stock": 18},
        {"id": "10", "name": "Lampara escritorio", "price": 19.99, "description": "Lampara LED regulable", "stock": 25},
    ]

    for p in productos:
        # cada producto se guarda como un hash product:<id>
        redis_client.hset(f"product:{p['id']}", mapping=p)


def mostrar_productos(redis_client):
    print("Productos guardados en Redis:")
    claves = sorted(redis_client.scan_iter("product:*"), key=lambda k: int(k.split(":")[1]))
    for clave in claves:
        p = redis_client.hgetall(clave)
        print(f"  {clave} -> {p['name']} | {p['price']} EUR | stock: {p['stock']} | {p['description']}")
    print(f"Total: {len(claves)} productos")


if __name__ == "__main__":
    try:
        redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        redis_client.ping()  # para ver que conecta antes de cargar nada

        # Inicializa los productos en Redis
        initialize_products(redis_client)
        print("¡Productos inicializados en Redis!")

        mostrar_productos(redis_client)

    except Exception as e:
        print(f"Error al conectarse a Redis: {e}")
