from abc import ABC, abstractmethod

# 1. Producto Abstracto
class OrdenBase(ABC):
    @abstractmethod
    def procesar_orden(self):
        pass

# 2. Productos Concretos
class OrdenRutinaria(OrdenBase):
    def procesar_orden(self):
        return {
            "sla_horas": 72, 
            "notificar_admin": False,
            "tipo_descripcion": "Mantenimiento programado o de baja criticidad."
        }

class OrdenCritica(OrdenBase):
    def procesar_orden(self):
        return {
            "sla_horas": 4, 
            "notificar_admin": True,
            "tipo_descripcion": "¡Alerta Roja! Requiere intervención inmediata del jefe de planta."
        }

# 3. La Fábrica (Factory Method)
class FabricaDeOrdenes:
    @staticmethod
    def crear_orden(prioridad: str) -> OrdenBase:
        prioridad = prioridad.lower()
        if prioridad in ['alta', 'critica']:
            return OrdenCritica()
        else:
            return OrdenRutinaria()