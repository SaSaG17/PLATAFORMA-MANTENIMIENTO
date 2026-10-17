# composite_activos.py
from abc import ABC, abstractmethod

class ActivoIndustrial(ABC):
    @abstractmethod
    def calcular_costo_mantenimiento(self) -> float:
        pass

class MaquinaIndividual(ActivoIndustrial):
    def __init__(self, nombre: str, costo_base: float):
        self.nombre = nombre
        self.costo_base = costo_base

    def calcular_costo_mantenimiento(self) -> float:
        return self.costo_base

class LineaProduccionComposite(ActivoIndustrial):
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.elementos = []

    def agregar(self, activo: ActivoIndustrial):
        self.elementos.append(activo)

    def calcular_costo_mantenimiento(self) -> float:
        total = sum(item.calcular_costo_mantenimiento() for item in self.elementos)
        return total