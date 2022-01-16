# API ENGINEER
### Almacenes:
1. warehouse_id = 1: California
2. warehouse_id = 2: San Fransisco

### Categorias:
1. product_qty = 1: All
2. product_qty = 2: Alimentos
3. product_qty = 3: Bebidas
4. product_qty = 4: Electrodomesticos		

## main_1:

Post -> Body -> Binary -> productos.json
Get  -> Actualiza la cantidad actual de productos, se obtiene el almacen 

## main_2:

1. Post -> Body -> Binary -> filtro_1.json, filtro_2.json, filtro_3.json
    * Al no encontrarse un producto en stock, no lo mostrara como resultado
    * Los resultados de los filtros estan en combinacion de Categoria y Almacen 
    * Actualiza la cantidad actual de productos
    * Se obtiene el almacen del producto
3. Get - > Body -> Binary -> pedido.json
    * Obtiene resultado como combinacion de Categoria, Almacen y Nombre
    * Reduce la cantidad de producto
    * De no haber en stock, mostrara mensaje
Se puede crear productos iguales en diferentes almacenes, modificar productos.json

## Dockerfile:
 * Archivo para correr en Google CLoud Plataform
