from flask import Flask, jsonify, request, render_template
import os
import redis

app = Flask(__name__)

# Conexion a Redis
# fase 0 -> "localhost" / fase 1 -> endpoint de ElastiCache
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
USE_SSL = os.environ.get("REDIS_SSL", "false").lower() == "true"  # poner a True si el cluster tiene cifrado en transito

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, ssl=USE_SSL, decode_responses=True)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/products', methods=['GET'])
def get_products():
    
    products = []
    # recorremos todas las claves product:* y sacamos cada hash
    for key in redis_client.scan_iter('product:*'):
        p = redis_client.hgetall(key)
        products.append({
            "id": p['id'],
            "name": p['name'],
            "price": float(p['price']),
            "description": p['description'],
            "stock": int(p['stock'])
        })
    products.sort(key=lambda x: int(x['id']))

    return jsonify(products)

@app.route('/cart', methods=['GET'])
def get_cart():
    
    cart_items = []
    for key in redis_client.scan_iter('cart:*'):
        item = redis_client.hgetall(key)
        cart_items.append({
            "id": item['id'],
            "name": item['name'],
            "price": float(item['price']),
            "quantity": int(item['quantity'])
        })
    cart_items.sort(key=lambda x: int(x['id']))

    return jsonify(cart_items)

@app.route('/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id') if data else None

    # comprobar que el producto existe
    if not product_id or not redis_client.exists(f'product:{product_id}'):
        return jsonify({"status": "error", "message": "El producto no existe"}), 404

    cart_key = f'cart:{product_id}'

    if redis_client.exists(cart_key):
        # ya estaba en la cesta -> sumamos 1
        redis_client.hincrby(cart_key, 'quantity', 1)
    else:
        # primera vez: copiamos los datos del producto a la cesta
        # (asi la cesta es independiente de la info original del producto)
        producto = redis_client.hgetall(f'product:{product_id}')
        redis_client.hset(cart_key, mapping={
            "id": product_id,
            "name": producto['name'],
            "price": producto['price'],
            "quantity": 1
        })

    return jsonify({"status": "added"})


@app.route('/checkout', methods=['POST'])
def checkout():
    comprados = []
    for key in redis_client.scan_iter('cart:*'):
        item = redis_client.hgetall(key)
        comprados.append(f"{item['name']} x{item['quantity']}")
        redis_client.delete(key)

    print("Compra procesada:", comprados)
    return jsonify({"status": "completed", "items": comprados})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
