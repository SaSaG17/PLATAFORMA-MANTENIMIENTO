# patron_builder.py

class Repuesto:
    def __init__(self):
        self.codigo_pieza = None
        self.nombre_repuesto = None
        self.stock_actual = 0
        self.stock_minimo = 5
        self.costo_unitario = 0.0

    def __str__(self):
        return f"{self.codigo_pieza} - {self.nombre_repuesto} (Stock: {self.stock_actual})"

class RepuestoBuilder:
    def __init__(self):
        self.repuesto = Repuesto()

    def set_codigo(self, codigo):
        self.repuesto.codigo_pieza = codigo
        return self

    def set_nombre(self, nombre):
        self.repuesto.nombre_repuesto = nombre
        return self

    def set_stock(self, stock):
        self.repuesto.stock_actual = int(stock) if stock else 0
        return self

    def set_stock_minimo(self, stock_min):
        self.repuesto.stock_minimo = int(stock_min) if stock_min else 5
        return self

    def set_costo(self, costo):
        self.repuesto.costo_unitario = float(costo) if costo else 0.0
        return self

    def build(self):
        """Retorna el objeto final ensamblado paso a paso"""
        return self.repuesto