from flask import Flask
from flask import request
from flask import jsonify

"""
Autenticacion Odoo
"""

url = 'http://localhost:8069'
db = 'myung'
username = 'nicksc1911@gmail.com'
password = '627488ef2874955dcdeca55098eb42c9f0988a96'
import xmlrpc.client

"""
Inicializacion de Modelo
"""

common = xmlrpc.client.ServerProxy('%s/xmlrpc/2/common' % url)
version = common.version()
print("details...", version)
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# Almacenes exitentes
almacenes = [" ", "Calif/Stock", "WH/Stock"]

# Inicializacion API
app = Flask(__name__)

# Funcion Ingresar Productos a las Bases de Datos
def ingresar_productos(productos):
    print(productos)
    print()
    print("Cantidad de Productos:",len(productos))

    for prod in productos:
        # Creacion de Productos
        vals_prod = [{
        'name': prod['name'], 
        'price':prod['price'], 
        'categ_id':prod['categ_id'], 
        'warehouse_id':prod['warehouse_id'], 
        'type':prod['type']
        }]
        models.execute_kw(db, uid, password, 'product.template', 'create', vals_prod)

        # Añadir inventario - Cantidad Inicial Disponible
        location_id = models.execute(db,uid,password,'stock.location','search',[('complete_name','=',almacenes[prod['warehouse_id']])])
        product_id = models.execute(db,uid,password,'product.product','search',[('name','=',prod['name'])])

        vals_inv_header = {
	        'name': prod['name'],
	        'prefill_counted_quantity': 'counted'
	    }
        inv_header = models.execute(db,uid,password,'stock.inventory','create',vals_inv_header)

        action_id = models.execute(db,uid,password,'stock.inventory','action_start',[inv_header])

        # Relacionar producto::inventario - Ingresar cantidad en ano inicia;
        vals_line = {
	        'inventory_id': inv_header,
	        'location_id': location_id[0],
	        'product_id': product_id[0],
	        'product_qty': prod["product_qty"]
        }
        models.execute(db,uid,password,'stock.inventory.line','create',vals_line)
        action_id = models.execute(db,uid,password,'stock.inventory','action_validate',[inv_header])

        # Asignacion de la cantidad
        product_id = models.execute(db,uid,password,'product.product','search',[('name','=',prod["name"] )])
        quant_id = models.execute(db,uid,password,'stock.quant','search',[('product_id','=',product_id[0])])

        vals_line = {           
	    'quantity': prod["product_qty"]
        }
        models.execute(db,uid,password,'stock.quant','write',quant_id,vals_line)
    pass

#Funcion lectura de Productos Existentes
def lectura_productos():
    #Obtencion de productos
    ps = models.execute_kw(db, uid, password,
    'product.product', 'search_read',[],
    {'fields': ['name', 'list_price', 'categ_id', 'warehouse_id', 'qty_available']})
    print(ps)
    prods = []

    # Incrementa el Almacen a la respuesta
    for p in ps:
        print(p['name'])
        a = models.execute_kw(db, uid, password,
        'stock.move', 'search_read',
        [[['product_id','=',p['name']]]],
        {'fields': ['location_dest_id']})

        print(a[-1]['location_dest_id'][1])
        p["warehouse_id"] = a[-1]['location_dest_id'][1]

        # Actualizando la cantidad de Producto 
        product_id = models.execute(db,uid,password,'product.product','search',[('name','=',p["name"] )])
        quant_id = models.execute(db,uid,password,'stock.quant','search',[('product_id','=',product_id[0])])
                
        a = models.execute_kw(db, uid, password,
        'stock.quant', 'search_read',
        [[['id','=',quant_id]]],
        {'fields': ['quantity']})
        print(a[-1])
        p["qty_available"] = a[-1]["quantity"]
        prods.append(p)
    return prods

"""Requests"""
@app.route('/products', methods = ["GET", "POST"])
def products_action():
    print(request.method)

    # Ingreso de productos
    if  (request.method == "POST"):
        ingresar_productos(request.json)
        return "productos ingresados"
    
    # Productos existentes
    else:
        ps = lectura_productos()
        return jsonify(ps)

app.run(debug = True)
