# patrones_estructurales/facade_cmms.py
from conexion import ConexionBaseDatos

class CMMSFacade:
    def evaluar_equipo_integral(self, nombre_equipo: str):
        conexion = ConexionBaseDatos.obtener_instancia().obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        
        resultado_diagnostico = {
            "equipo": nombre_equipo,
            "sensor_encontrado": False,
            "estado_sensor": "Desconocido",
            "tiene_ordenes_activas": False,
            "detalle_orden": None,
            "estado_general": "Normal",
            "mensaje": ""
        }

        try:
            # 1. Consultar el sensor por su nombre o código para obtener su ID real
            sql_sensor = """
                SELECT id, codigo_sensor, nombre_equipo, tipo_variable, estado, actualizado_en 
                FROM sensores 
                WHERE nombre_equipo = %s OR codigo_sensor = %s 
                LIMIT 1
            """
            cursor.execute(sql_sensor, (nombre_equipo, nombre_equipo))
            sensor = cursor.fetchone()

            if sensor:
                resultado_diagnostico["sensor_encontrado"] = True
                resultado_diagnostico["estado_sensor"] = sensor["estado"]
                resultado_diagnostico["tipo_variable"] = sensor["tipo_variable"]
                sensor_id = sensor["id"]

                # 2. Buscar en 'ordenes_trabajo' usando el 'sensor_id' exacto y que esté pendiente
                sql_ot = """
                    SELECT id, sensor_id, titulo, descripcion, prioridad, estado, sla_horas 
                    FROM ordenes_trabajo 
                    WHERE sensor_id = %s AND LOWER(estado) != 'completada'
                    LIMIT 1
                """
                cursor.execute(sql_ot, (sensor_id,))
                orden = cursor.fetchone()

                if orden:
                    resultado_diagnostico["tiene_ordenes_activas"] = True
                    resultado_diagnostico["detalle_orden"] = orden

            # 3. Lógica de Decisión Unificada de la Fachada
            if resultado_diagnostico["tiene_ordenes_activas"]:
                resultado_diagnostico["estado_general"] = "Alerta Crítica / Con Orden Activa"
                ot_info = resultado_diagnostico["detalle_orden"]
                resultado_diagnostico["mensaje"] = (
                    f"Atención: El sensor tiene una Orden de Trabajo activa (#{ot_info['id']}: {ot_info['titulo']}) "
                    f"con prioridad '{ot_info['prioridad']}' y estado '{ot_info['estado']}'."
                )
            elif sensor and sensor["estado"].lower() in ["alerta", "fallo", "peligro", "inactivo"]:
                resultado_diagnostico["estado_general"] = "Alerta en Sensor"
                resultado_diagnostico["mensaje"] = (
                    f"El sensor {sensor['codigo_sensor']} reporta un estado crítico: {sensor['estado']}."
                )
            else:
                resultado_diagnostico["estado_general"] = "Operativo / Normal"
                resultado_diagnostico["mensaje"] = (
                    f"El equipo {nombre_equipo} se encuentra operando correctamente. Sin órdenes de trabajo pendientes."
                )

        except Exception as e:
            resultado_diagnostico["estado_general"] = "Error de Consulta"
            resultado_diagnostico["mensaje"] = f"No se pudo consultar la base de datos: {e}"
        finally:
            cursor.close()

        return resultado_diagnostico