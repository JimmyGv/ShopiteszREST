import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse,Response,Any
from models import PedidoInsert, PedidoPay, PedidoCancelado,PedidosConsulta, PedidoConsById
from dao import Conexion

app = FastAPI()

#Evento que indica el momento en que se crea una conexion con la base de datos 
@app.on_event('startup')
def startup():
    app.cn=Conexion()
    print("Conectando a la base de datos")

@app.on_event('shutdown')
def shutdown():
    app.cn.cerrar()
    print("Desconectando de la base de datos")

@app.get('/categorias')
def consultaGeneralCategorias():
    return app.cn.consultaCategorias()

#Ruta de inicio

@app.get("/")
def inicio():
    return {"message": "Bienvenido a pedidos rest"}

@app.post('/pedidos')
def agregarPedido(pedido: PedidoInsert):
    #res=app.cn.agregarPedido(pedido)
    salida =app.cn.agregarPedido(pedido)
    return salida
    #return{"mensaje":"Se agrego el pedido correctamente"}

@app.put('/pedidos/{idPedido}/pagar')
def  pagar_pedido(idPedido:str,pedidoPay:PedidoPay) :
    #return{"mensaje":f"Pagando el pedido con el id:{idPedido}"}
    salida = app.cn.pagarPedido(idPedido,pedidoPay)
    return salida

@app.delete('/pedidos/{idPedido}/cancelar')
def cancelar_pedido(idPedido: str,pedidoCacnelado:PedidoCancelado):
    salida = app.cn.cancelarPedido(idPedido,pedidoCacnelado)
    return salida
    #return{"mensaje":f"Cancelando el pedido con id: {idPedido}"}

@app.get('/pedidos',response_model=PedidosConsulta)
def consultaGeneralOfPedidos()->Any:
    salida = app.cn.consultaGeneralPedidos()
    #lista=[{"idPedido":"1","total":"140"},{"idPedido":"4","total":"99"},{"idPedido":"5","total":"989.98089"}]
    return PedidosConsulta(**salida)
@app.get('/pedidos/vendedor/{idVendedor}')
def consultaIndividualOfPedido(idVendedor:int):
    salida = app.cn.consultaPedidosVendedor(idVendedor)
    #lista=[{"idPedido":"1","total":"140"},{"idPedido":"4","total":"99"},{"idPedido":"5","total":"989.98089"}]
    return salida