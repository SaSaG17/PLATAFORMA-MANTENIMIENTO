# patrones_comportamiento/state_usuarios.py
from abc import ABC, abstractmethod

# ==========================================
# PATRÓN STATE - ESTADO DEL USUARIO (EMPLEADO)
# ==========================================

# 1. Estado Abstracto
class EstadoUsuario(ABC):
    """
    Define las decisiones que dependen del estado laboral del empleado
    (columna 'estado' de la tabla usuarios: 'activo' / 'inactivo').
    """
    nombre_bd = ""

    @abstractmethod
    def puede_iniciar_sesion(self) -> bool:
        pass

    @abstractmethod
    def puede_recibir_ordenes(self) -> bool:
        pass

    @abstractmethod
    def mensaje_restriccion(self) -> str:
        pass

# 2. Estados Concretos
class UsuarioActivo(EstadoUsuario):
    nombre_bd = "activo"

    def puede_iniciar_sesion(self) -> bool:
        return True

    def puede_recibir_ordenes(self) -> bool:
        return True

    def mensaje_restriccion(self) -> str:
        return ""

class UsuarioInactivo(EstadoUsuario):
    nombre_bd = "inactivo"

    def puede_iniciar_sesion(self) -> bool:
        return False

    def puede_recibir_ordenes(self) -> bool:
        return False

    def mensaje_restriccion(self) -> str:
        return "Tu cuenta se encuentra inactiva. Comunícate con el administrador de planta."

# 3. Contexto (el objeto cuyo comportamiento cambia según su estado)
class ContextoUsuario:
    """
    Recibe el valor crudo de la BD y delega las decisiones en el estado actual.
    Un valor vacío (NULL) se interpreta como 'activo', igual que el DEFAULT de la tabla.
    """
    _ESTADOS = {
        "activo": UsuarioActivo,
        "inactivo": UsuarioInactivo
    }

    def __init__(self, estado_bd: str = None):
        clave = (estado_bd or "activo").strip().lower()
        self._estado = self._ESTADOS.get(clave, UsuarioInactivo)()

    @property
    def estado_actual(self) -> str:
        return self._estado.nombre_bd

    def puede_iniciar_sesion(self) -> bool:
        return self._estado.puede_iniciar_sesion()

    def puede_recibir_ordenes(self) -> bool:
        return self._estado.puede_recibir_ordenes()

    def mensaje_restriccion(self) -> str:
        return self._estado.mensaje_restriccion()
