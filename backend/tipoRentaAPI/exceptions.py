# tipoRentaAPI/exceptions.py
from core.exceptions import BaseCustomException
from rest_framework import status


class TipoRentaNotFound(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'El tipo de renta no existe.'
    default_code = 'tipo_renta_not_found'


class TipoRentaAlreadyExists(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Ya existe un tipo de renta con este nombre.'
    default_code = 'tipo_renta_already_exists'


class InvalidPriceForUnit(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El precio por unidad debe ser mayor a cero.'
    default_code = 'invalid_price_for_unit'


class InvalidDuration(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La duración predeterminada debe ser mayor a cero.'
    default_code = 'invalid_duration'


class InactiveTipoRenta(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Este tipo de renta está inactivo.'
    default_code = 'inactive_tipo_renta'


class TipoRentaInUse(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'No se puede eliminar este tipo de renta porque está siendo utilizado.'
    default_code = 'tipo_renta_in_use'