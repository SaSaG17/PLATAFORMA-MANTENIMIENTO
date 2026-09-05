# PLATAFORMA MANTENIMIENTO
# Sandra Milena Albarracin Gualdron
# Patrones Software Grupo E195
Este repositorio contiene el diseño e implementación de una Plataforma de Mantenimiento Predictivo, enfocada en el monitoreo de sensores en equipos industriales, la detección temprana de fallas mediante Machine Learning, la gestión de órdenes de trabajo y la integración con un inventario de repuestos. El proyecto busca mejorar el seguimiento del estado de los equipos, detectar posibles fallas antes de que ocurran y facilitar la planificación y gestión de las actividades de mantenimiento.

🎯 Objetivo del Proyecto
- Monitorear el estado de los equipos industriales mediante datos obtenidos de sensores.
- Detectar posibles fallas de manera temprana utilizando modelos de Machine Learning.
- Gestionar las órdenes de trabajo relacionadas con el mantenimiento de los equipos.
- Controlar la disponibilidad y uso de los repuestos necesarios para las actividades de mantenimiento.
# ⚙️ Plataforma de Mantenimiento Predictivo Industrial (CMMS)

Sistema Web desarrollado en **Flask (Python)** y **MySQL** para la gestión inteligente del mantenimiento industrial. La plataforma integra monitoreo de variables de sensores en tiempo real, control de acceso basado en roles (RBAC) y flujos avanzados automatizados mediante patrones de diseño de software.

---

## 🚀 Características Principales y Arquitectura

El software está construido bajo estrictos principios de diseño modular y buenas prácticas de ingeniería de software:

1. **Patrón Singleton (`conexion.py`):**
   * Centraliza y gestiona una única instancia de conexión a la base de datos MySQL durante todo el ciclo de vida de la aplicación web.
   * Evita la saturación de conexiones concurrentes y optimiza el rendimiento del servidor.

2. **Control de Acceso Basado en Roles - RBAC (`/login` y `/usuarios`):**
   * **Administrador:** Control absoluto sobre altas, modificaciones de estado laboral y asignación de roles (`administrador`, `mantenimiento`, `operario`).
   * **Personal Técnico/Operativo:** Acceso restringido y enfocado al monitoreo de equipos y actualización de incidencias.

3. **Patrón Factory Method (`patron_factory.py` & Módulo de Órdenes de Trabajo):**
   * Desacopla la capa de presentación (rutas de Flask) de las reglas de negocio industriales.
   * Calcula de forma dinámica el **SLA (Service Level Agreement / Acuerdo de Nivel de Servicio)** y los protocolos de notificación según la criticidad de la falla reportada (*Orden Rutinaria* vs. *Orden Crítica*).

---

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3.x, Flask
* **Base de Datos:** MySQL, `mysql-connector-python`
* **Frontend:** Bootstrap 5, HTML5, Jinja2
* **Control de Versiones:** Git
