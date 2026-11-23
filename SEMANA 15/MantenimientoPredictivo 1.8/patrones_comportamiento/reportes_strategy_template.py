from abc import ABC, abstractmethod
from datetime import datetime


# ==============================================================================
# 1. PATRÓN STRATEGY: Estrategias de Filtrado Dinámico
# Propósito: Encapsular cada criterio de filtro en su propia clase para
# intercambiarlos en ejecución sin llenar las rutas de condicionales.
# ==============================================================================

class EstrategiaFiltro(ABC):
    """Interfaz base para las estrategias de filtrado de registros."""

    @abstractmethod
    def filtrar(self, registros: list, criterio: str) -> list:
        pass


class FiltroEmpleadoPorCargo(EstrategiaFiltro):
    """Filtra empleados/usuarios según su rol/cargo."""

    def filtrar(self, registros: list, criterio: str) -> list:
        if not criterio or criterio.strip().lower() == "todos":
            return registros
        criterio_limpio = criterio.strip().lower()
        return [
            emp for emp in registros
            if str(emp.get("cargo", "")).strip().lower() == criterio_limpio
        ]


class FiltroOrdenPorEmpleado(EstrategiaFiltro):
    """Filtra órdenes de trabajo por el empleado asignado."""

    def filtrar(self, registros: list, criterio: str) -> list:
        if not criterio or not criterio.strip():
            return registros
        criterio_limpio = criterio.strip().lower()
        return [
            ot for ot in registros
            if criterio_limpio in str(ot.get("empleado", "")).lower()
        ]


class FiltroOrdenPorRepuesto(EstrategiaFiltro):
    """Filtra órdenes de trabajo según el repuesto utilizado."""

    def filtrar(self, registros: list, criterio: str) -> list:
        if not criterio or not criterio.strip():
            return registros
        criterio_limpio = criterio.strip().lower()
        return [
            ot for ot in registros
            if criterio_limpio in str(ot.get("repuesto", "")).lower()
        ]


class FiltroOrdenPorEquipo(EstrategiaFiltro):
    """Filtra órdenes de trabajo por el equipo o sensor asociado."""

    def filtrar(self, registros: list, criterio: str) -> list:
        if not criterio or not criterio.strip():
            return registros
        criterio_limpio = criterio.strip().lower()
        return [
            ot for ot in registros
            if criterio_limpio in str(ot.get("equipo_sensor", "")).lower()
        ]


# ==============================================================================
# 2. PATRÓN TEMPLATE METHOD: Flujo Estándar de Generación de Reportes
# Propósito: Definir el flujo fijo de generación de reportes (consultar BD ->
# filtrar -> formatear -> calcular resumen) delegando cada paso a la subclase.
# ==============================================================================

class GeneradorReporteTemplate(ABC):
    """Clase abstracta con el método plantilla generar_reporte()."""

    def __init__(self, estrategia_filtro: EstrategiaFiltro = None):
        self._estrategia = estrategia_filtro

    def set_estrategia(self, estrategia_filtro: EstrategiaFiltro):
        """Permite cambiar la estrategia de filtrado en ejecución."""
        self._estrategia = estrategia_filtro

    def generar_reporte(self, criterio_filtro: str = None) -> dict:
        """Template Method: ejecuta el flujo completo del reporte."""
        registros_bd = self.obtener_datos_bd()

        if self._estrategia and criterio_filtro:
            registros_filtrados = self._estrategia.filtrar(registros_bd, criterio_filtro)
        else:
            registros_filtrados = registros_bd

        registros_formateados = self.formatear_registros(registros_filtrados)
        resumen = self.calcular_resumen(registros_formateados)

        return {
            "titulo_reporte": self.obtener_titulo(),
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filtro_aplicado": criterio_filtro if criterio_filtro else "Todos",
            "registros": registros_formateados,
            "resumen": resumen,
        }

    @abstractmethod
    def obtener_titulo(self) -> str:
        pass

    @abstractmethod
    def obtener_datos_bd(self) -> list:
        pass

    @abstractmethod
    def formatear_registros(self, registros: list) -> list:
        pass

    @abstractmethod
    def calcular_resumen(self, registros: list) -> dict:
        pass


class ReporteEmpleados(GeneradorReporteTemplate):
    """Reporte de Gestión de Empleados a partir de la tabla `usuarios`."""

    def __init__(self, consulta_fn, estrategia: EstrategiaFiltro = None):
        super().__init__(estrategia)
        self._consulta_fn = consulta_fn

    def obtener_titulo(self) -> str:
        return "Informe de Gestión de Empleados"

    def obtener_datos_bd(self) -> list:
        return self._consulta_fn()

    def formatear_registros(self, registros: list) -> list:
        salida = []
        for fila in registros:
            estado_str = str(fila.get("estado", "")).strip().lower()
            activo_bool = estado_str == "activo"
            salida.append({
                "nombre": fila.get("nombre", ""),
                "cargo": fila.get("cargo", ""),
                "activo": activo_bool,
                "estado_texto": "Activo" if activo_bool else "Inactivo",
            })
        return salida

    def calcular_resumen(self, registros: list) -> dict:
        total = len(registros)
        activos = sum(1 for r in registros if r["activo"])
        return {
            "total": total,
            "activos": activos,
            "inactivos": total - activos,
        }


class ReporteOrdenesTrabajo(GeneradorReporteTemplate):
    """Reporte de Órdenes de Trabajo a partir de `ordenes_trabajo`, `sensores` y `usuarios`."""

    def __init__(self, consulta_fn, estrategia: EstrategiaFiltro = None):
        super().__init__(estrategia)
        self._consulta_fn = consulta_fn

    def obtener_titulo(self) -> str:
        return "Informe de Órdenes de Trabajo"

    def obtener_datos_bd(self) -> list:
        return self._consulta_fn()

    def formatear_registros(self, registros: list) -> list:
        salida = []
        for fila in registros:
            costo_val = fila.get("costo")
            salida.append({
                "numero_orden": fila.get("numero_orden", ""),
                "equipo_sensor": fila.get("equipo_sensor", ""),
                "empleado": fila.get("empleado", ""),
                "titulo": fila.get("titulo", ""),
                "estado": fila.get("estado", ""),
                "repuesto": fila.get("repuesto") or "No especificado",
                "costo": float(costo_val) if costo_val is not None else 0.0,
            })
        return salida

    def calcular_resumen(self, registros: list) -> dict:
        costo_total = sum(r["costo"] for r in registros)
        return {
            "total_ordenes": len(registros),
            "costo_total": round(costo_total, 2),
        }