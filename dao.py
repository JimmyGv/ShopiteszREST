from pymongo import MongoClient
from models import PedidoInsert, PedidoCancelado
from datetime import datetime
from models import PedidoPay,Envio
from bson import ObjectId
from models import PedidoInsert, PedidoCancelado, PedidoPay, Envio, detalleProducto, Paqueteria

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
    def cancelarPedido(self,idPedido,cancelacion:PedidoCancelado):
        pedido=self.pedidos.find_one({"_id":ObjectId(idPedido)},projection={"estatus":True})
        resp = {"estatus":"","mensaje":""}
        if pedido:
            if pedido['estatus']=="Captura" or pedido['estatus']=="Pagado":
                res=self.bd.pedidos.update_one({"_id":ObjectId(idPedido)},{"$set":cancelacion.dict})
                if pedido['estatus']=="Pagado":
                    self.bd.pedidos.update_one({"_id":ObjectId(idPedido)},{"$set":{"pago.status":"Devolucion"}})    
                resp["estatus"]="OK"
                resp["mensaje"]=f'Pedido con id: {idPedido} se ha cancelado con exito'
            resp["estatus"]= "Error"
            resp["mensaje"]= "Error al cancelar el pedido, el pedido no existe o ya ha sido enviado"
        else:
            resp["estatus"]= "Error"
            resp["mensaje"]= "Error al cancelar el pedido, el pedido no existe o no se encuentra en captura"
        return resp
    
    def consultaGeneralPedidos(self):
        resp={"estatus":"","mensaje":""}
        resultado=self.bd.consultaPedidos.find()
        resp["estatus"]="OK"
        resp["mensaje"]="Listado de pedidos"
        lista=[]
        for pedido in resultado:
            pedido["idPedido"]=str(pedido["idPedido"])
            detalleTemp=[]
            detalles=pedido['detalles']
            for detalle in detalles:
                detalle=self.complementarDetalle(detalle)
                detalleTemp.append(detalle)
            pedido['detalles']=detalleTemp
            if 'pago' in pedido:
                pago=pedido['pago']
                pago['noTarjeta']=self.consultarNoTarjeta(pago['idTarjeta'])
                pedido['pago']=pago
            lista.append(pedido)
        resp["pedidos"]=lista
        return resp
    def consultarProducto(self,idProducto):
        producto=self.bd.productos.find_one({"_id":idProducto})
        return producto
    def complementarDetalle(self,detalle):
        prod=self.consultarProducto(detalle['idProducto'])
        detalle['nombreProducto']=prod['nombre']
        return detalle
    def consultarNoTarjeta(self,idTarjeta):
        res=self.bd.usuarios.find_one({"tarjetas.idTarjeta":idTarjeta},projection={"tarjetas.$":True,"_id":0})
        print(res)
        tarjetas=res['tarjetas']
        tarjeta=tarjetas[0]
        return tarjeta["noTarjeta"]
    def consultaPedidosVendedor(self,idVendedor):
        resp={"estatus":"","mensaje":""}
        resultado=self.bd.consultaPedidos.find({"vendedor.idVendedor":idVendedor})
        resp["estatus"]="OK"
        resp["mensaje"]="Listado de pedidos"
        lista=[]
        for pedido in resultado:
            pedido["idPedido"]=str(pedido["idPedido"])
            detalleTemp=[]
            detalles=pedido['detalles']
            for detalle in detalles:
                detalle=self.complementarDetalle(detalle)
                detalleTemp.append(detalle)
            pedido['detalles']=detalleTemp
            if 'pago' in pedido:
                pago=pedido['pago']
                pago['noTarjeta']=self.consultarNoTarjeta(pago['idTarjeta'])
                pedido['pago']=pago
            if 'envio' in pedido:
                envio=pedido['envio']
                envio['paqueteria']['nombre']= self.consultarNombrePaqueteria(envio['paqueteria']['idPaqueteria'])
                detalleEnvio = envio['detalle']
                for det in detalleEnvio:
                    name =self.consultarProducto(det['idProducto'])
                    det['nombreProducto']= name['nombre']
                envio['detalle']=detalleEnvio
                pedido['envio']=envio
            lista.append(pedido)
            print(lista)
        resp["pedido"]=lista
        return resp
    def consultarNombrePaqueteria(self,idPaqueteria):
        res=self.bd.paqueterias.find_one({"_id":idPaqueteria},projection={"_id":0})
        return res['nombre']
    