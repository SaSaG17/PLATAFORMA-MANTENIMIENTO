import copy

class PrototipoIntervencion:
    def __init__(self, tipo_equipo="General", tareas_base=None, repuestos_sugeridos=None):
        self.tipo_equipo = tipo_equipo
        self.tareas_base = tareas_base or ["Inspección visual", "Limpieza de componentes", "Prueba de encendido"]
        self.repuestos_sugeridos = repuestos_sugeridos or []
        self.observaciones_tecnico = ""

    def clonar(self):
        """Aplica el Patrón Prototype clonando profundamente el objeto base"""
        return copy.deepcopy(self)

# Banco de prototipos preconfigurados para clonación rápida
REGISTRO_PROTOTIPOS = {
    "bomba": PrototipoIntervencion(
        tipo_equipo="Bomba Hidráulica",
        tareas_base=["Revisión de sellos mecánicos", "Lubricación de rodamientos", "Prueba de presión"],
        repuestos_sugeridos=["Sello de Goma", "Grasa Industrial"]
    ),
    "sensor": PrototipoIntervencion(
        tipo_equipo="Sensor de Temperatura",
        tareas_base=["Calibración de escala", "Verificación de cableado", "Prueba de señal PLC"],
        repuestos_sugeridos=["Conector Bornera"]
    )
}