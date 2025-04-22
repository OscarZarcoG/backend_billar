# clienteAPI/exceptions.py
from core.exceptions import BaseCustomException
from rest_framework import status

class ClienteAlreadyExists(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'El cliente ya existe.'
    default_code = 'cliente_already_exists'

class ClienteNotFound(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'El cliente no existe.'
    default_code = 'cliente_not_found'

class ClienteInactive(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El cliente está inactivo.'
    default_code = 'cliente_inactive'

class InvalidClienteStatus(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El estado del cliente no es válido.'
    default_code = 'invalid_cliente_status'

class InvalidFrequencyType(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El tipo de frecuencia no es válido.'
    default_code = 'invalid_frequency_type'