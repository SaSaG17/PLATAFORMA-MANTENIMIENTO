# adapter_sensores.py

class SensorIoTExterno:
    """Sistema externo de sensores con una interfaz diferente."""
    def obtener_lectura_formato_externo(self):
        return {
            "device_id": "PUMP_04_EXT",
            "status_code": 5,  # 5 significa fallo crítico
            "message": "Sobrecalentamiento severo detectado"
        }

class InterfazSensorInterno:
    """Interfaz estándar que espera tu sistema CMMS."""
    def leer_estado(self):
        pass

class AdaptadorSensorIoT(InterfazSensorInterno):
    """Adapta la API externa al estándar del CMMS."""
    def __init__(self, sensor_externo: SensorIoTExterno):
        self.sensor_externo = sensor_externo

    def leer_estado(self):
        datos_externos = self.sensor_externo.obtener_lectura_formato_externo()
        # Traduce el formato externo al formato interno del CMMS
        return {
            "codigo_equipo": datos_externos["device_id"],
            "criticidad": "Alta" if datos_externos["status_code"] >= 5 else "Baja",
            "descripcion": datos_externos["message"]
        }