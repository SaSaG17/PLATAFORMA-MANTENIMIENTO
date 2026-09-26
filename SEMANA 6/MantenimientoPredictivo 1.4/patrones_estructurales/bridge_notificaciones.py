# bridge_notificaciones.py
from abc import ABC, abstractmethod

# 1. Implementador (Canal de Envío)
class CanalEnvio(ABC):
    @abstractmethod
    def enviar_mensaje(self, destinatario: str, mensaje: str):
        pass

class EnvioCorreo(CanalEnvio):
    def enviar_mensaje(self, destinatario: str, mensaje: str):
        print(f"[CORREO A {destinatario}]: {mensaje}")

class EnvioWhatsApp(CanalEnvio):
    def enviar_mensaje(self, destinatario: str, mensaje: str):
        print(f"[WHATSAPP A {destinatario}]: {mensaje}")

# 2. Abstracción (Tipo de Notificación)
class Notificacion(ABC):
    def __init__(self, canal: CanalEnvio):
        self.canal = canal

    @abstractmethod
    def notificar(self, destinatario: str, asunto: str):
        pass

class NotificacionAlertaCritica(Notificacion):
    def notificar(self, destinatario: str, asunto: str):
        mensaje = f"¡ALERTA CRÍTICA DE MANTENIMIENTO! - {asunto}"
        self.canal.enviar_mensaje(destinatario, mensaje)