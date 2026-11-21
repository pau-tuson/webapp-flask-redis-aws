# Tienda online con Flask y Redis en AWS

Backend de una tienda online sencilla hecho en **Python con Flask**, que guarda los productos y la cesta de la compra en **Redis**. La app se desplegó en **AWS**: Flask en una instancia **EC2** y Redis primero en la misma EC2 y después en un clúster de **Amazon ElastiCache**.

Práctica de la asignatura *Sistemes Distribuïts* (Grado en Ingeniería Informática, UAB, curso 2026-27).

## Qué hace

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Página de la tienda (HTML + JS) |
| GET | `/products` | Lista de productos leída de Redis |
| GET | `/cart` | Contenido de la cesta |
| POST | `/cart` | Añade un producto a la cesta (`{"product_id": "3"}`); si ya estaba, suma 1 con `HINCRBY` |
| POST | `/checkout` | Procesa la compra y vacía la cesta |

**Modelo de datos en Redis:** cada producto es un hash `product:<id>` y cada línea de la cesta un hash `cart:<id>`. Para recorrer las claves se usa `SCAN` (`scan_iter`) en lugar de `KEYS`, para no bloquear el servidor cuando hay muchas claves.

## Tecnologías

Python · Flask · Redis · AWS EC2 · Amazon ElastiCache · API REST · JavaScript (frontend)

## Cómo ejecutarlo en local

```bash
pip install -r requirements.txt
# Redis en local (por ejemplo con Docker)
docker run -d -p 6379:6379 redis
python initialize_redis.py   # carga 10 productos de prueba
python app.py                # http://localhost:5000
```

Para usar un Redis remoto (por ejemplo ElastiCache), basta con definir variables de entorno:

```bash
export REDIS_HOST=<endpoint-de-elasticache>
export REDIS_PORT=6379
export REDIS_SSL=true   # si el clúster tiene cifrado en tránsito
```

## Mi parte

El frontend (`static/` y `templates/`) lo daba la asignatura. Yo implementé el backend: los endpoints de la API, el modelo de datos en Redis y el script de carga, y el despliegue en AWS con EC2, ElastiCache y los grupos de seguridad.
