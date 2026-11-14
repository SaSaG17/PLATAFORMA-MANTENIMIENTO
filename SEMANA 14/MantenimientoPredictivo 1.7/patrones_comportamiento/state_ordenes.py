# patrones_comportamiento/state_ordenes.py
from abc import ABC, abstractmethod

# ==========================================
# PATRÓN STATE - CICLO DE VIDA DE LA ORDEN DE TRABAJO
# ==========================================

class TransicionInvalidaError(Exception):
    """Se lanza cuando se intenta una acción no permitida en el estado actual."""
    pass

# 1. Estado Abstracto
class EstadoOrden(ABC):
    """
    Estados alineados con el enum de la BD: ordenes_trabajo.estado
    ('pendiente', 'en_proceso', 'completada'). No requiere modificar la tabla.
    """
    nombre_bd = ""
    etiqueta = ""

    @abstractmethod
    def asignar(self, contexto):
        pass

    @abstractmethod
    def iniciar(self, contexto):
        pass

    @abstractmethod
    def completar(self, contexto):
        pass

# 2. Estados Concretos
class OrdenPendiente(EstadoOrden):
    nombre_bd = "pendiente"
    etiqueta = "Pendiente"

    def asignar(self, contexto):
        # Permitido: no cambia de estado, solo se (re)asigna el responsable
        pass

    def iniciar(self, contexto):
        contexto._establecer_estado(OrdenEnProceso())

    def completar(self, contexto):
        # Cierre directo: conserva el comportamiento original de /ordenes/ejecutar
        contexto._establecer_estado(OrdenCompletada())

class OrdenEnProceso(EstadoOrden):
    nombre_bd = "en_proceso"
    etiqueta = "En Proceso"

    def asignar(self, contexto):
        raise TransicionInvalidaError("No se puede reasignar una orden que ya está en proceso.")

    def iniciar(self, contexto):
        raise TransicionInvalidaError("La orden ya fue iniciada.")

    def completar(self, contexto):
        contexto._establecer_estado(OrdenCompletada())

class OrdenCompletada(EstadoOrden):
    nombre_bd = "completada"
    etiqueta = "Completada"

    def asignar(self, contexto):
        raise TransicionInvalidaError("No se puede asignar una orden completada.")

    def iniciar(self, contexto):
        raise TransicionInvalidaError("No se puede iniciar una orden completada.")

    def completar(self, contexto):
        raise TransicionInvalidaError("La orden ya fue completada anteriormente.")

# 3. Contexto
class ContextoOrden:
    """
    Envuelve el valor de 'estado' leído de la BD y expone las acciones del ciclo de vida.
    Las rutas Flask ya no comparan strings: le preguntan al contexto qué está permitido.
    """
    _ESTADOS = {
        "pendiente": OrdenPendiente,
        "en_proceso": OrdenEnProceso,
        "completada": OrdenCompletada
    }

    def __init__(self, estado_bd: str = None):
        clave = (estado_bd or "pendiente").strip().lower()
        self._estado = self._ESTADOS.get(clave, OrdenPendiente)()

    def _establecer_estado(self, nuevo_estado: EstadoOrden):
        self._estado = nuevo_estado

    @property
    def estado_actual(self) -> str:
        return self._estado.nombre_bd

    @property
    def etiqueta(self) -> str:
        return self._estado.etiqueta

    # Acciones del ciclo de vida (lanzan TransicionInvalidaError si no aplican)
    def asignar(self):
        self._estado.asignar(self)

    def iniciar(self):
        self._estado.iniciar(self)

    def completar(self):
        self._estado.completar(self)

    # Consultas seguras (para habilitar/ocultar botones y guardas de las rutas)
    def _permite(self, accion) -> bool:
        probe = ContextoOrden(self.estado_actual)
        try:
            getattr(probe, accion)()
            return True
        except TransicionInvalidaError:
            return False

    def puede_asignarse(self) -> bool:
        return self._permite("asignar")

    def puede_iniciarse(self) -> bool:
        return self._permite("iniciar")

    def puede_cerrarse(self) -> bool:
        return self._permite("completar")
