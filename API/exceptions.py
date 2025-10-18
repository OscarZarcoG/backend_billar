from rest_framework import status
from rest_framework.exceptions import APIException


class BaseCustomException(APIException):
    status_code = None
    default_detail = None
    default_code = None

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        super().__init__(detail=detail, code=code)


class PasswordMismatch(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Las contraseñas no coinciden.'
    default_code = 'password_mismatch'


class PasswordRequired(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La contraseña es requerida.'
    default_code = 'password_required'


class StockInsuficiente(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No hay suficiente stock disponible.'
    default_code = 'stock_insuficiente'


class MesaOcupada(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La mesa ya está ocupada.'
    default_code = 'mesa_ocupada'


class CajaAbierta(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Ya hay una caja abierta.'
    default_code = 'caja_abierta'


class CajaCerrada(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La caja está cerrada.'
    default_code = 'caja_cerrada'


class AlquilerNoActivo(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El alquiler no está activo.'
    default_code = 'alquiler_no_activo'


class PagoInsuficiente(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El pago es insuficiente.'
    default_code = 'pago_insuficiente'


class ProductoInactivo(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El producto está inactivo.'
    default_code = 'producto_inactivo'


class ConfiguracionNoModificable(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La configuración no es modificable.'
    default_code = 'configuracion_no_modificable'