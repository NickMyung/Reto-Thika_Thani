Almacenes:
 -> warehouse_id = 1: California
 -> warehouse_id = 2: San Fransisco

Categorias:
 -> product_qty = 1: All
 -> product_qty = 2: Alimentos
 -> product_qty = 3: Bebidas
 -> product_qty = 4: Electrodomesticos		

main_1:

Post -> Body -> Binary -> productos.json

main_2:

Post -> Body -> Binary -> filtro_1.json, filtro_2.json, filtro_3.json
Get - > Body -> Binary -> pedido.json