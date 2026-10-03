# PLATAFORMA MANTENIMIENTO
# Sandra Milena Albarracin Gualdron
# Patrones Software Grupo E195
Este repositorio contiene el diseño e implementación de una Plataforma de Mantenimiento Predictivo, enfocada en el monitoreo de sensores en equipos industriales, la detección temprana de fallas mediante Machine Learning, la gestión de órdenes de trabajo y la integración con un inventario de repuestos. El proyecto busca mejorar el seguimiento del estado de los equipos, detectar posibles fallas antes de que ocurran y facilitar la planificación y gestión de las actividades de mantenimiento.

🎯 Objetivo del Proyecto
- Monitorear el estado de los equipos industriales mediante datos obtenidos de sensores.
- Detectar posibles fallas de manera temprana utilizando modelos de Machine Learning.
- Gestionar las órdenes de trabajo relacionadas con el mantenimiento de los equipos.
- Controlar la disponibilidad y uso de los repuestos necesarios para las actividades de mantenimiento.
# ⚙️ Plataforma de Mantenimiento Predictivo Industrial 

Sistema Web desarrollado en **Flask (Python)** y **MySQL** para la gestión inteligente del mantenimiento industrial. La plataforma integra monitoreo de variables de sensores en tiempo real, control de acceso basado en roles (RBAC) y flujos avanzados automatizados mediante patrones de diseño de software.

---

## 🚀 Características Principales y Arquitectura

El software está construido integrando los siguientes patrones de diseño y módulos funcionales:

### 1. Patrón Singleton (`conexion.py`)
* **Instancia Única:** Centraliza y gestiona una única conexión persistente a la base de datos MySQL durante todo el ciclo de vida de la aplicación web en Flask.
* **Optimización:** Evita la saturación de conexiones concurrentes y optimiza el rendimiento general del servidor.

### 2. Control de Acceso Basado en Roles - RBAC (`/login` y `/usuarios`)
* **Administrador:** Control absoluto sobre altas, modificaciones de estado laboral y asignación de roles (`administrador`, `mantenimiento`, `operario`).
* **Personal Técnico/Operativo:** Acceso restringido y enfocado al monitoreo de equipos y actualización de incidencias.

### 3. Patrón Factory Method (`patron_factory.py` & Módulo de Órdenes de Trabajo)
* Desacopla la capa de presentación de las reglas de negocio industriales.
* Calcula de forma dinámica el SLA (Service Level Agreement) y los protocolos de notificación según la criticidad de la falla reportada (*Orden Rutinaria* vs. *Orden Crítica*).

### 4. Patrones Estructurales (`patrones_estructurales/`)
Para robustecer la arquitectura frente a la integración de hardware, notificaciones, jerarquías de planta y reportes, se implementaron cuatro patrones estructurales clave:

* **Adapter (`adapter_sensores.py`):** 
  * Permite integrar sensores IoT y dispositivos de telemetría externos con estructuras de datos incompatibles, traduciéndolas de forma transparente al formato estándar del CMMS.
  * *Ruta de prueba:* `http://127.0.0.1:5000/probar-adapter`

* **Bridge (`bridge_notificaciones.py`):** 
  * Desacopla los tipos de avisos (como alertas críticas) de sus canales físicos de envío (como WhatsApp, correos o SMS), permitiendo combinarlos libremente en tiempo de ejecución.
  * *Ruta de prueba:* `http://127.0.0.1:5000/probar-bridge`

* **Composite (`composite_activos.py`):** 
  * Modela la infraestructura de planta en forma de una jerarquía de árbol. Permite tratar de forma uniforme tanto a una máquina individual como a una línea de producción completa para calcular costos de mantenimiento de forma recursiva.
  * *Ruta de prueba:* `http://127.0.0.1:5000/probar-composite`

* **Decorator (`decorator_ordenes.py`):** 
  * Enuelve dinámicamente las órdenes de trabajo base al momento de imprimirlas, añadiendo elementos especiales al vuelo (como sellos de auditoría o certificaciones ISO) sin alterar la base de datos.
  * *Ruta de prueba:* `http://127.0.0.1:5000/probar-decorator/<int:orden_id>`

---

## 📁 Estructura del Proyecto

```text
CMMS_PROJECT/
│
├── patrones_estructurales/
│   ├── adapter_sensores.py
│   ├── bridge_notificaciones.py
│   ├── composite_activos.py
│   └── decorator_ordenes.py
│
├── conexion.py                 # Patrón Singleton
├── patron_factory.py           # Patrón Factory Method
├── app.py                      # Archivo principal de rutas (Flask)
├── requirements.txt            # Dependencias del proyecto
└── README.md

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3.x, Flask
* **python app.py Para iniciar servidor Flask
* **Base de Datos:** MySQL, `mysql-connector-python`
* **Frontend:** Bootstrap 5, HTML5, Jinja2
* **Control de Versiones:** Git
