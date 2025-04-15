# mesasAPI/responses.py
from rest_framework import status
from core.responses import BaseSuccessResponse


class MesaCreatedSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="Mesa creada satisfactoriamente", data=data)
        self.status_code = status.HTTP_201_CREATED


class MesaUpdatedSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="Mesa actualizada exitosamente", data=data)
        self.status_code = status.HTTP_200_OK


class MesaDeletedSuccess(BaseSuccessResponse):
    def __init__(self):
        super().__init__(message="Mesa eliminada exitosamente")
        self.status_code = status.HTTP_204_NO_CONTENT


class TipoRentaCreatedSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="Tipo de renta creada exitosamente", data=data)
        self.status_code = status.HTTP_201_CREATED


class TipoRentaUpdatedSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="Tipo de renta actualizado exitosamente", data=data)
        self.status_code = status.HTTP_200_OK

class TipoRentaDeletedSuccess(BaseSuccessResponse):
    def __init__(self):
        super().__init__(message="Tipo de renta eliminado exitosamente")
        self.status_code = status.HTTP_204_NO_CONTENT


class MesaStateChangedSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="Estado de mesa cambiado exitosamente", data=data)
        self.status_code = status.HTTP_200_OK

class ReservationCreatedSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="Reserva creada exitosamente", data=data)
        self.status_code = status.HTTP_201_CREATED