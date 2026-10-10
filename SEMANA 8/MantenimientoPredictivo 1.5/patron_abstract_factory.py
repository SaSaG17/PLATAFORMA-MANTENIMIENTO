from abc import ABC, abstractmethod

class DocumentoMovimiento(ABC):
    @abstractmethod
    def calcular_nuevo_stock(self, stock_actual, cantidad):
        pass
    
    @abstractmethod
    def obtener_tipo(self):
        pass

class MovimientoEntrada(DocumentoMovimiento):
    def calcular_nuevo_stock(self, stock_actual, cantidad):
        return stock_actual + cantidad

    def obtener_tipo(self):
        return "ENTRADA"

class MovimientoSalida(DocumentoMovimiento):
    def calcular_nuevo_stock(self, stock_actual, cantidad):
        if stock_actual < cantidad:
            raise ValueError("Stock insuficiente para procesar la salida.")
        return stock_actual - cantidad

    def obtener_tipo(self):
        return "SALIDA"

class FabricaMovimientoInventario(ABC):
    @abstractmethod
    def crear_documento(self) -> DocumentoMovimiento:
        pass

class FabricaEntradaInventario(FabricaMovimientoInventario):
    def crear_documento(self) -> DocumentoMovimiento:
        return MovimientoEntrada()

class FabricaSalidaInventario(FabricaMovimientoInventario):
    def crear_documento(self) -> DocumentoMovimiento:
        return MovimientoSalida()