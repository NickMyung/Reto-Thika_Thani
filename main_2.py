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
almacenes_id = {"":"", "California":"Calif/Stock","San Fransisco":"WH/Stock"}

# Inicializacion API
app = Flask(__name__)

# Funcion de Filtro segun almacen y categoria
def lectura_productos(filtros):
    print("Filtros:",filtros)

    #Obtencion de productos
    ps = models.execute_kw(db, uid, password,
    'product.product', 'search_read',[],
    {'fields': ['name', 'list_price', 'categ_id', 'warehouse_id', 'qty_available']})
    print(ps)
    prods = []

    # Filtro
    for p in ps:
        if (p['categ_id'][1] == ("All / "+filtros[0]["Categoria"]) or filtros[0]["Categoria"] == ""): # Puede ignorar el campo de Categoria
            print(p['name'])
            a = models.execute_kw(db, uid, password,
            'stock.move', 'search_read',
            [[['product_id','=',p['name']]]],
            {'fields': ['location_dest_id']})
	    
	    # Ubicacion del almacen
            print(a[-1]['location_dest_id'][1])
            p["warehouse_id"] = a[-1]['location_dest_id'][1]
            
            if (p["warehouse_id"] == almacenes_id[filtros[0]["Almacen"]] or almacenes_id[filtros[0]["Almacen"]] == ""): # Puede ignorar el campo de Almacen

                # Actualizando la cantidad de Producto 
                product_id = models.execute(db,uid,password,'product.product','search',[('name','=',p["name"] )])
                quant_id = models.execute(db,uid,password,'stock.quant','search',[('product_id','=',product_id[0])])
                
                a = models.execute_kw(db, uid, password,
                'stock.quant', 'search_read',
                [[['id','=',quant_id]]],
                {'fields': ['quantity']})
                print(a[-1])

                # Si no hay producto en stock, no mostrar resultado
                if a[-1]["quantity"] >0:
                    p["qty_available"] = a[-1]["quantity"]
                    prods.append(p)
    return prods

#Funcion Seleccion de Productoss
def seleccion_productos(pedidos):
    print("Pedidos:",pedidos)

    # Obtencion de productos
    ps = models.execute_kw(db, uid, password,
    'product.product', 'search_read',[],
    {'fields': ['name', 'list_price', 'categ_id', 'warehouse_id', 'qty_available']})
    print(ps)
    prods = []

    # Incrementa el Almacen a la respuesta
    for p in ps:
        if (p['categ_id'][1] == ("All / "+pedidos[0]["Categoria"])): # Categoria
            print(p['name'])
            a = models.execute_kw(db, uid, password,
            'stock.move', 'search_read',
            [[['product_id','=',p['name']]]],
            {'fields': ['location_dest_id']})
	    
	    # Ubicacion del almacen
            print(a[-1]['location_dest_id'][1])
            p["warehouse_id"] = a[-1]['location_dest_id'][1]

            if (p["warehouse_id"] == almacenes_id[pedidos[0]["Almacen"]]): # Almacen
                if (p["name"] == pedidos[0]["Nombre"]): # Nombre

                    # Obteniendo producto y reduciendo cantidad 
                    product_id = models.execute(db,uid,password,'product.product','search',[('name','=',p["name"] )])
                    quant_id = models.execute(db,uid,password,'stock.quant','search',[('product_id','=',product_id[0])])

                    a = models.execute_kw(db, uid, password,
                    'stock.quant', 'search_read',
                    [[['id','=',quant_id]]],
                    {'fields': ['quantity']})
                    print(a[-1])

                    # Si no hay producto en stock, no mostrar resultado
                    if a[-1]["quantity"] == 0:
                        return []

                    p["qty_available"] = a[-1]["quantity"]-1

                    vals_line = {           
	                'quantity': p["qty_available"]
                    }
                    models.execute(db,uid,password,'stock.quant','write',quant_id,vals_line)
                    
                    prods.append(p)
    return prods

"""Requests"""
@app.route('/obtener/producto', methods = ["GET", "POST"])
def products_action():
    print(request.method)

    # LEctura de productos acorde a los filtros
    if  (request.method == "POST"):
        ps = lectura_productos(request.json)
        return jsonify(ps)
    
    # seleccion de producto para compra
    else:
        ps = seleccion_productos(request.json)
        if len(ps) == 0: # Sin productos para mostrar
            return "Producto no disponible"
        return jsonify(ps)

app.run(debug = True)
