from pymongo import MongoClient
from models import PedidoInsert, DetallePedido
from datetime import datetime
from models import PedidoPay
from bson import ObjectId

class Conexion():
    def __init__(self):
        self.cliente=MongoClient()
        self.bd=self.cliente.ShopiteszREST
    def cerrar(self):
        self.cliente.close()
    def consultaCategorias(self):
        return list(self.bd.categorias.find())
    def agregarPedido(self,pedido:PedidoInsert):
        respuesta={"estatus":"error" , "mensaje":"msg"}
        if(pedido.idComprador!=pedido.idVendedor):
            if self.comprobarUsuario(pedido.idComprador,"Comprador")>0 and self.comprobarUsuario(pedido.idVendedor,"Vendedor")>0:
                ban = True
                for dp in pedido.detalles:    
                    if self.comprobarProducto(dp.idProducto,pedido.idVendedor,dp.cantidad)==0:
                        ban =False
                        break
                if ban:
                    res=self.bd.pedidos.insert_one(pedido.dict())
                    respuesta["estatus"]="OK"
                    respuesta["mensaje"]="Pedido agregado con exito con id: " + str(res.inserted_id)
                    respuesta["pedido"]= pedido
                else:
                    respuesta["estatus"]= "error"
                    respuesta["mensaje"]="No se puede realizar un pedido a un producto que no existe o la cantidad es insuficiente"
            else:
                respuesta["estatus"]= "error"
                respuesta["mensaje"]="No se puede realizar un pedido a un usuario que no existe"
        else:
            respuesta["estatus"]="error"
            respuesta["mensaje"]="No se puede realizar un pedido a si mismo"
        return respuesta
    def comprobarUsuario(self, idUsuario,tipo):
        cont = self.bd.usuarios.count_documents({"_id":idUsuario,"tipo":tipo})
        return cont
    def comprobarProducto(self,idProducto,idVendedor,cantidad):
        cont = self.bd.productos.count_documents({"_id":idProducto,"idVendedor":idVendedor,"existencia":{"$gte":cantidad}})
        return cont
    def pagarPedido(self, idPedido, pedidoPay:PedidoPay):
        pedido=self.comprobarPedido(idPedido)
        resp = {"estatus":"","mensaje":""}
        if pedido:
            if pedido['total']==pedidoPay.pago.monto:
                cont=self.comprobarTarjeta(pedidoPay.pago.idTarjeta,pedido['idComprador'])
                if cont>0:
                    res=self.bd.pedidos.update_one({"_id":ObjectId(idPedido)},{"$set":pedidoPay.dict()})
                    if res.modified_count>0:
                        resp["estatus"]="OK"
                        resp["mensaje"]=f'Pedido con id: {idPedido} se ha pagado con exito'
                    else:
                        resp['estatus']= "Error"
                        resp["mensaje"]=f'Pedido con id: {idPedido} no se ha podido pagar intentelo mas tarde'
                else:
                    resp["estatus"]= "Error"
                    resp["mensaje"]=f'Pedido con id: {idPedido} no se ha podido pagar, la tarjeta no existe o esta vencida'
            else:
                resp['estatus']= "Error"
                resp["mensaje"]="Error al efecuar al pago, el monto no cubre la cantidad requerida"
        else:
            resp["estatus"]= "Error"
            resp["mensaje"]= "Error al efectuar el pago, el pedido no existe o no se encuentra en captura"
        return resp
        
    def comprobarTarjeta(self,idTarjeta, idComprador):
        fechaActual=datetime.now()
        cont=self.bd.usuarios.count_documents({"_id":idComprador,"tarjetas.idTarjeta":idTarjeta,"tarjetas.estatus":'A',"tarjetas.fechaVencimiento":{"$gte":fechaActual}})
        return cont
    def comprobarPedido(self, idPedido):
        pedido=self.bd.pedidos.find_one({"_id":ObjectId(idPedido),"estatus":"Captura"},projection={"idComprador":True, "total":True})
        return pedido