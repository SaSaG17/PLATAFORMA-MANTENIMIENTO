# patrones_comportamiento/visitor_repuestos.py
from abc import ABC, abstractmethod

# ==========================================
# PATRÓN VISITOR - OPERACIONES SOBRE EL INVENTARIO DE REPUESTOS
# ==========================================

# 1. Visitante Abstracto (cada operación nueva es un visitante nuevo)
class VisitanteInventario(ABC):
    @abstractmethod
    def visitar_repuesto(self, repuesto):
        pass

    @abstractmethod
    def obtener_resultado(self) -> dict:
        pass

# 2. Elemento Abstracto
class ElementoInventario(ABC):
    @abstractmethod
    def aceptar(self, visitante: VisitanteInventario):
        pass

# 3. Elemento Concreto (refleja la tabla 'repuestos')
class RepuestoInventario(ElementoInventario):
    def __init__(self, id_repuesto, codigo_pieza, nombre_repuesto, stock_actual, stock_minimo, costo_unitario):
        self.id_repuesto = id_repuesto
        self.codigo_pieza = codigo_pieza
        self.nombre_repuesto = nombre_repuesto
        self.stock_actual = int(stock_actual)
        self.stock_minimo = int(stock_minimo)
        self.costo_unitario = float(costo_unitario)

    def aceptar(self, visitante: VisitanteInventario):
        visitante.visitar_repuesto(self)

# 4. Estructura de objetos que se recorre
class InventarioRepuestos:
    def __init__(self):
        self.elementos = []

    def agregar(self, elemento: ElementoInventario):
        self.elementos.append(elemento)

    @classmethod
    def desde_filas(cls, filas: list):
        """Construye la colección a partir de las filas de 'SELECT * FROM repuestos'."""
        inventario = cls()
        for fila in filas:
            inventario.agregar(RepuestoInventario(
                fila["id"], fila["codigo_pieza"], fila["nombre_repuesto"],
                fila["stock_actual"], fila["stock_minimo"], fila["costo_unitario"]
            ))
        return inventario

    def aceptar(self, visitante: VisitanteInventario) -> dict:
        for elemento in self.elementos:
            elemento.aceptar(visitante)
        return visitante.obtener_resultado()

# 5. Visitantes Concretos
class VisitanteValorInventario(VisitanteInventario):
    """Calcula el valor económico del inventario (stock_actual x costo_unitario)."""
    def __init__(self):
        self.detalle = []
        self.valor_total = 0.0

    def visitar_repuesto(self, repuesto: RepuestoInventario):
        subtotal = round(repuesto.stock_actual * repuesto.costo_unitario, 2)
        self.valor_total += subtotal
        self.detalle.append({
            "codigo_pieza": repuesto.codigo_pieza,
            "nombre_repuesto": repuesto.nombre_repuesto,
            "stock_actual": repuesto.stock_actual,
            "costo_unitario": repuesto.costo_unitario,
            "subtotal": subtotal
        })

    def obtener_resultado(self) -> dict:
        return {
            "valor_total": round(self.valor_total, 2),
            "total_referencias": len(self.detalle),
            "detalle": self.detalle
        }

class VisitanteReposicion(VisitanteInventario):
    """
    Detecta los repuestos en o por debajo del stock mínimo (mismo criterio que repuestos.html)
    y sugiere cuántas unidades comprar para volver al doble del mínimo.
    """
    def __init__(self):
        self.a_reponer = []
        self.costo_estimado = 0.0

    def visitar_repuesto(self, repuesto: RepuestoInventario):
        if repuesto.stock_actual <= repuesto.stock_minimo:
            cantidad_sugerida = (repuesto.stock_minimo * 2) - repuesto.stock_actual
            costo = round(cantidad_sugerida * repuesto.costo_unitario, 2)
            self.costo_estimado += costo
            self.a_reponer.append({
                "codigo_pieza": repuesto.codigo_pieza,
                "nombre_repuesto": repuesto.nombre_repuesto,
                "stock_actual": repuesto.stock_actual,
                "stock_minimo": repuesto.stock_minimo,
                "cantidad_sugerida": cantidad_sugerida,
                "costo_estimado": costo
            })

    def obtener_resultado(self) -> dict:
        return {
            "total_a_reponer": len(self.a_reponer),
            "costo_estimado": round(self.costo_estimado, 2),
            "detalle": self.a_reponer
        }
