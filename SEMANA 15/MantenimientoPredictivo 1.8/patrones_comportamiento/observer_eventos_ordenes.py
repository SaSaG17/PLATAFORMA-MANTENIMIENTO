# patrones_comportamiento/observer_eventos_ordenes.py
from abc import ABC, abstractmethod
from conexion import ConexionBaseDatos
from patrones_estructurales.bridge_notificaciones import (
    CanalEnvio, EnvioCorreo, Notificacion, NotificacionAlertaCritica
)

# ==========================================
# PATRÓN OBSERVER - EVENTOS DEL CICLO DE VIDA DE LA ORDEN DE TRABAJO
# ==========================================

EVENTO_ORDEN_CREADA = "orden_creada"
EVENTO_ORDEN_ASIGNADA = "orden_asignada"
EVENTO_ORDEN_COMPLETADA = "orden_completada"


# ------------------------------------------
# Consultas de apoyo (los observadores resuelven sus propios datos a partir del id)
# ------------------------------------------
def _consultar(sql: str, parametros: tuple = (), todos: bool = False):
    conexion = ConexionBaseDatos.obtener_instancia().obtener_conexion()
    if not conexion:
        return [] if todos else None
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(sql, parametros)
        return cursor.fetchall() if todos else cursor.fetchone()
    finally:
        cursor.close()

def _obtener_orden(orden_id):
    return _consultar(
        "SELECT id, titulo, prioridad, asignado_a, requiere_notificacion_admin FROM ordenes_trabajo WHERE id = %s",
        (orden_id,)
    )

def _obtener_usuario(usuario_id):
    return _consultar("SELECT id, nombre, email FROM usuarios WHERE id = %s", (usuario_id,))

def _obtener_administradores():
    return _consultar(
        "SELECT id, nombre, email FROM usuarios WHERE rol = 'administrador' AND estado = 'activo'",
        todos=True
    )


# ------------------------------------------
# Nuevas abstracciones del Bridge (reutilizan CanalEnvio sin modificar el archivo original)
# ------------------------------------------
class NotificacionAsignacion(Notificacion):
    def notificar(self, destinatario: str, asunto: str):
        self.canal.enviar_mensaje(destinatario, f"NUEVA ORDEN DE TRABAJO ASIGNADA - {asunto}")

class NotificacionInformativa(Notificacion):
    def notificar(self, destinatario: str, asunto: str):
        self.canal.enviar_mensaje(destinatario, f"AVISO DE MANTENIMIENTO - {asunto}")


# ------------------------------------------
# 1. Observador Abstracto
# ------------------------------------------
class ObservadorOrden(ABC):
    @abstractmethod
    def actualizar(self, evento: str, datos: dict):
        pass


# ------------------------------------------
# 2. Sujeto (Bus de Eventos)
# ------------------------------------------
class BusEventosOrdenes:
    """
    Sujeto del patrón Observer: mantiene la lista de suscriptores por evento y los notifica.
    Un observador que falle nunca interrumpe el flujo principal de la ruta ni a los demás observadores.
    """
    def __init__(self):
        self._suscriptores = {}

    def suscribir(self, evento: str, observador: ObservadorOrden):
        self._suscriptores.setdefault(evento, []).append(observador)

    def desuscribir(self, evento: str, observador: ObservadorOrden):
        if observador in self._suscriptores.get(evento, []):
            self._suscriptores[evento].remove(observador)

    def publicar(self, evento: str, datos: dict):
        print(f"📣 [OBSERVER] Evento publicado: {evento} -> {datos}")
        for observador in list(self._suscriptores.get(evento, [])):
            try:
                observador.actualizar(evento, datos)
            except Exception as e:
                print(f"⚠️ [OBSERVER] {observador.__class__.__name__} falló al procesar '{evento}': {e}")


# ------------------------------------------
# 3. Observadores Concretos
# ------------------------------------------
class NotificadorTecnico(ObservadorOrden):
    """Avisa al empleado asignado (usa el Bridge: abstracción de aviso + canal de envío)."""
    def __init__(self, canal: CanalEnvio):
        self.notificacion = NotificacionAsignacion(canal)

    def actualizar(self, evento: str, datos: dict):
        orden = _obtener_orden(datos["orden_id"])
        if not orden:
            return
        tecnico = _obtener_usuario(orden["asignado_a"])
        if tecnico:
            self.notificacion.notificar(
                tecnico["email"],
                f"OT #{orden['id']}: {orden['titulo']} (prioridad {orden['prioridad']})"
            )

class NotificadorAdmin(ObservadorOrden):
    """
    Avisa a los administradores activos cuando:
    - se crea una orden con requiere_notificacion_admin = 1 (la Factory la marca para alta/crítica), o
    - se completa una orden de prioridad alta o crítica.
    """
    def __init__(self, canal: CanalEnvio):
        self.alerta_critica = NotificacionAlertaCritica(canal)
        self.aviso = NotificacionInformativa(canal)

    def actualizar(self, evento: str, datos: dict):
        orden = _obtener_orden(datos["orden_id"])
        if not orden:
            return

        if evento == EVENTO_ORDEN_CREADA and orden["requiere_notificacion_admin"]:
            notificacion = self.alerta_critica
            asunto = f"Se creó la OT #{orden['id']} '{orden['titulo']}' con prioridad {orden['prioridad']}"
        elif evento == EVENTO_ORDEN_COMPLETADA and orden["prioridad"] in ("alta", "critica"):
            notificacion = self.aviso
            asunto = f"Se completó la OT #{orden['id']} '{orden['titulo']}' (prioridad {orden['prioridad']})"
        else:
            return

        for admin in _obtener_administradores():
            notificacion.notificar(admin["email"], asunto)

class RegistroAuditoria(ObservadorOrden):
    """Guarda el historial de cambios de las órdenes en la tabla auditoria_ordenes."""
    _SQL_TABLA = """
        CREATE TABLE IF NOT EXISTS auditoria_ordenes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            orden_id INT NOT NULL,
            evento VARCHAR(30) NOT NULL,
            usuario_id INT NULL,
            detalle VARCHAR(255) NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """

    def __init__(self):
        self._tabla_lista = False

    def actualizar(self, evento: str, datos: dict):
        conexion = ConexionBaseDatos.obtener_instancia().obtener_conexion()
        if not conexion:
            return
        cursor = conexion.cursor()
        try:
            if not self._tabla_lista:
                cursor.execute(self._SQL_TABLA)
                self._tabla_lista = True
            cursor.execute(
                "INSERT INTO auditoria_ordenes (orden_id, evento, usuario_id, detalle) VALUES (%s, %s, %s, %s)",
                (datos["orden_id"], evento, datos.get("usuario_id"), datos.get("detalle"))
            )
            conexion.commit()
        finally:
            cursor.close()


# ------------------------------------------
# Instancia global con las suscripciones ya configuradas (requerida por app.py)
# ------------------------------------------
bus_eventos_global = BusEventosOrdenes()

_canal_correo = EnvioCorreo()
_notificador_tecnico = NotificadorTecnico(_canal_correo)
_notificador_admin = NotificadorAdmin(_canal_correo)
_registro_auditoria = RegistroAuditoria()

bus_eventos_global.suscribir(EVENTO_ORDEN_CREADA, _notificador_tecnico)
bus_eventos_global.suscribir(EVENTO_ORDEN_CREADA, _notificador_admin)
bus_eventos_global.suscribir(EVENTO_ORDEN_CREADA, _registro_auditoria)

bus_eventos_global.suscribir(EVENTO_ORDEN_ASIGNADA, _notificador_tecnico)
bus_eventos_global.suscribir(EVENTO_ORDEN_ASIGNADA, _registro_auditoria)

bus_eventos_global.suscribir(EVENTO_ORDEN_COMPLETADA, _notificador_admin)
bus_eventos_global.suscribir(EVENTO_ORDEN_COMPLETADA, _registro_auditoria)
