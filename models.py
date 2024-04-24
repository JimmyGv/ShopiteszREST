from pydantic import BaseModel,Field
from datetime import datetime


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