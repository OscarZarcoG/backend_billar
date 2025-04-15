# reservasAPI/responses.py
from rest_framework import status
from core.responses import BaseSuccessResponse


class ReservaCreatedSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="Reserva creada exitosamente", data=data)
        self.status_code = status.HTTP_201_CREATED


class ReservaUpdatedSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="Reserva actualizada exitosamente", data=data)
        self.status_code = status.HTTP_200_OK


class ReservaDeletedSuccess(BaseSuccessResponse):
    def __init__(self):
        super().__init__(message="Reserva eliminada exitosamente")
        self.status_code = status.HTTP_204_NO_CONTENT


class ReservaConfirmedSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="Reserva confirmada exitosamente", data=data)
        self.status_code = status.HTTP_200_OK


class ReservaCanceledSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="Reserva cancelada exitosamente", data=data)
        self.status_code = status.HTTP_200_OK


class ReservaCompletedSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="Reserva completada exitosamente", data=data)
        self.status_code = status.HTTP_200_OK


class ReservaListSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="Lista de reservas obtenida exitosamente", data=data)
        self.status_code = status.HTTP_200_OK


class ReservaDetailSuccess(BaseSuccessResponse):
    def __init__(self, data=None):
        super().__init__(message="Detalles de reserva obtenidos exitosamente", data=data)
        self.status_code = status.HTTP_200_OK