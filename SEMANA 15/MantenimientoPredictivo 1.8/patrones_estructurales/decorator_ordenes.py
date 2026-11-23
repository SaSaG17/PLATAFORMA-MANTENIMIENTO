# decorator_ordenes.py
from abc import ABC, abstractmethod

class OrdenImprimible(ABC):
    @abstractmethod
    def obtener_texto_impresion(self) -> str:
        pass

class OrdenTrabajoBase(OrdenImprimible):
    def __init__(self, id_orden: str, descripcion: str):
        self.id_orden = id_orden
        self.descripcion = descripcion

    def obtener_texto_impresion(self) -> str:
        return f"Orden #{self.id_orden}: {self.descripcion}"

class DecoratorOrden(OrdenImprimible):
    def __init__(self, orden: OrdenImprimible):
        self._orden = orden

    def obtener_texto_impresion(self) -> str:
        return self._orden.obtener_texto_impresion()

class DecoradorSelloAuditoria(DecoratorOrden):
    def obtener_texto_impresion(self) -> str:
        texto_base = super().obtener_texto_impresion()
        sello = "\n[✔ APROBADO] - Certificado bajo Normativa ISO de Auditoría de Planta."
        return texto_base + sello