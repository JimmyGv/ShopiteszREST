from pydantic import BaseModel,Field
from datetime import datetime
from typing import List, Optional

class DetallePedido(BaseModel):
    idProducto: int
    cantidad: int
    precio: float
    subtotal: float
    costoEnvio: float=Field(...,ge=0)
    subtotalEnvio: float=Field(...,ge=0)

class PedidoInsert(BaseModel):
    idComprador: int
    idVendedor: int
    fechaRegistro:datetime=Field(default=datetime.today())
    costosEnvio: float= Field(...,ge=0)
    subtotal: float= Field(...,gt=0) 
    total: float= Field(...,gt=0)
    estatus: str= Field(default='Captura')
    detalles: list[DetallePedido]

class Pago(BaseModel):
    fecha: datetime
    monto: float
    idTarjeta: int
    estatus: str

class PedidoPay(BaseModel):
    estatus:str
    pago:Pago

class PedidoCancelado(BaseModel):
    estatus:str=Field(default="Cancelado")
    motivoCancelacion:str

class DetallePedidoConsulta(BaseModel):
    idProducto:int
    cantidad:int
    precio:float
    subtotal:float
    costoEnvio:float
    subtotalEnvio:float
    nombreProducto:str  
class PagoConsulta(BaseModel): 
    fecha:datetime
    monto:float
    idTarjeta:int
    estatus:str
    noTarjeta:str

class Comprador(BaseModel):
    idComprador:int
    nombre:str

class Vendedor(BaseModel):
    idVendedor:int
    nombre:str

class Pedido(BaseModel):
    idPedido:str
    fechaRegistro:datetime=None
    fechaConfirmacion:datetime|None=None
    fechaCierre:datetime|None=None
    costosEnvio:float
    subtotal:float
    total:float
    estatus:str
    motivoCancelacion:str|None=None
    valoracion:int|None=None
    detalles:list[DetallePedido]
    pago:PagoConsulta|None=None
    comprador:Comprador
    vendedor:Vendedor

class PedidosConsulta(BaseModel):
    estatus:str
    mensaje:str
    pedidos:list[Pedido]

class Pedido(BaseModel):
    idPedido:str
    fechaRegistro:datetime=None
    fechaConfirmacion:datetime|None=None
    fechaCierre:datetime|None=None
    costosEnvio:float
    subtotal:float
    total:float
    estatus:str
    motivoCancelacion:str|None=None
    valoracion:int|None=None
    detalles:list[DetallePedido]
    pago:PagoConsulta|None=None
    comprador:Comprador
    vendedor:Vendedor

class DetallePedido(BaseModel):
    idProducto: int
    nombreProducto:str
    cantidad: int
    precio: float
    subtotal: float
    costoEnvio: float=Field(...,ge=0)
    subtotalEnvio: float=Field(...,ge=0)

class Paqueteria(BaseModel):
    idPaqueteria:int
    nombre:str

class DetailEnvio(BaseModel):
    idProducto:int
    nombreProducto:str
    cantidadEnviada:int
    cantidadRecibida:int
    comentario:str

class Envio(BaseModel):
    fechaSalida:datetime
    fechaEntPlan:datetime
    fechaRecepcion:datetime
    noGuia:str
    paqueteria:Paqueteria
    detalles:list[DetailEnvio]

class detalleProducto(BaseModel):
    idProducto:int
    nombreProducto:str
    cantidadEnviada:int
    cantidadRecibida:int
    comentario:str

class PedidoVendedor(BaseModel):
    idPedido:str
    fechaRegistro:datetime=None
    fechaConfirmacion:datetime|None=None
    fechaCierre:datetime|None=None
    costosEnvio:float
    subtotal:float
    total:float
    estatus:str
    motivoCancelacion:str|None=None
    valoracion:int|None=None
    detalles:list[DetallePedido]
    pago:PagoConsulta|None=None
    comprador:Comprador
    vendedor:Vendedor
    envio:Envio|None=None
    
class PedidoConsById(BaseModel):
    estatus:str
    mensaje:str
    pedido:list[PedidoVendedor]