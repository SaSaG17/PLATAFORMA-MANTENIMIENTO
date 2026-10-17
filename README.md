# PLATAFORMA DE MANTENIMIENTO PREDICTIVO (CMMS)
**Autora:** Sandra Milena Albarracín Gualdrón  
**Curso:** Patrones Software - Grupo E195  
**Institución:** Unidades Tecnológicas de Santander (UTS)

Este repositorio contiene el diseño e implementación de una Plataforma de Mantenimiento Predictivo (CMMS), enfocada en el monitoreo avanzado de sensores en equipos industriales, la detección temprana de fallas mediante un módulo de Machine Learning optimizado, la gestión de órdenes de trabajo, control de inventario de repuestos y analítica en tiempo real.

---

## 🎯 Objetivo del Proyecto
- Monitorear el estado y la telemetría de los equipos industriales mediante datos estructurados de sensores.
- Detectar posibles fallas de manera temprana utilizando modelos de Machine Learning con Lazy Loading y Caching.
- Gestionar las órdenes de trabajo relacionadas con el mantenimiento preventivo y correctivo de la planta.
- Controlar la disponibilidad y uso de los repuestos necesarios para las actividades técnicas.
- Proveer un panel analítico integral unificando subsistemas mediante interfaces desacopladas.

---

## ⚙️ Arquitectura y Tecnologías
Sistema web desarrollado en **Python (Flask)** y **MySQL**, integrando control de acceso basado en roles (RBAC) y flujos avanzados automatizados mediante patrones de diseño de software.

- **Backend:** Python 3.x, Flask
- **Base de Datos:** MySQL, `mysql-connector-python`
- **Frontend & Analítica:** Bootstrap 5, HTML5, Jinja2, Chart.js
- **Machine Learning & Optimización:** Módulos personalizados con gestión de caché y optimización de memoria RAM.

---

## 🚀 Características Principales y Patrones de Diseño

El software está construido integrando los siguientes patrones de diseño y módulos funcionales:

### 1. Patrón Singleton (`conexion.py`)
- **Instancia Única:** Centraliza y gestiona una única conexión persistente a la base de datos MySQL durante todo el ciclo de vida de la aplicación web en Flask.
- **Optimización:** Evita la saturación de conexiones concurrentes y optimiza el rendimiento general del servidor.

### 2. Control de Accesso Basado en Roles - RBAC (`/login` y `/usuarios`)
- **Administrador:** Control absoluto sobre altas, modificaciones de estado laboral y asignación de roles (`administrador`, `mantenimiento`, `operario`).
- **Personal Técnico/Operativo:** Acceso restringido y enfocado al monitoreo de equipos y actualización de incidencias.

### 3. Patrón Factory Method (`patron_factory.py` y Módulo de Órdenes de Trabajo)
- Desacopla la capa de presentación de las reglas de negocio industrial.
- Calcula de forma dinámica el SLA (*Service Level Agreement*) y los protocolos de notificación según la criticidad de la falla reportada (*Orden Rutinaria* vs. *Orden Crítica*).

### 4. Patrones Estructurales Clave (`patrones_estructurales/`)
Para robustecer la arquitectura frente a la integración de hardware, notificaciones, jerarquías de planta, analítica de IA y reportes, se implementaron patrones estructurales avanzados:

- **Adaptador (`adapter_sensores.py`):**
  - Permite integrar sensores IoT y dispositivos de telemetría externos con estructuras de datos incompatibles, traduciéndolas al formato estándar del CMMS.
  - *Ruta de prueba:* `http://127.0.0.1:5000/probar-adapter`
- **Puente (`bridge_notificaciones.py`):**
  - Desacopla los tipos de avisos (como alertas críticas) de sus canales físicos de envío (como WhatsApp o correos), permitiendo combinarlos libremente en ejecución.
  - *Ruta de prueba:* `http://127.0.0.1:5000/probar-bridge`
- **Compuesto (`composite_activos.py`):**
  - Modela la infraestructura de planta en forma de jerarquía de árbol. Trata de forma uniforme a una máquina individual o a una línea de producción completa para calcular costos de mantenimiento de forma recursiva.
  - *Ruta de prueba:* `http://127.0.0.1:5000/probar-composite`
- **Decorador (`decorator_ordenes.py`):**
  - Enuelve dinámicamente las órdenes de trabajo base al momento de imprimirlas, agregando elementos especiales al vuelo (sellos de auditoría o certificaciones ISO) sin alterar la base de datos.
  - *Ruta de prueba:* `http://127.0.0.1:5000/probar-decorator/<int:orden_id>`
- **Proxy (`patron_proxy_flyweight_ml.py`):**
  - Controla el acceso al motor analítico de Machine Learning mediante **Lazy Loading** (carga diferida del modelo pesado) y **Caching** (almacenamiento temporal de predicciones para respuestas instantáneas).
- **Flyweight (`patron_proxy_flyweight_ml.py`):**
  - Optimiza el consumo de memoria RAM separando el estado intrínseco (umbrales y unidades compartidas por tipo de variable) del estado extrínseco (lecturas puntuales de sensores), evitando la duplicación de objetos pesados.
- **Facade (`facade_cmms.py`):**
  - Centraliza y simplifica la interacción entre las vistas web y los múltiples subsistemas del backend, permitiendo cruzar de forma transparente el estado de los sensores, diagnósticos de IA y órdenes de trabajo activas bajo una interfaz unificada.

---

## 📁 Estructura del Proyecto
```text
CMMS_PROJECT/
│
├── patrones_estructurales/
│   ├── adapter_sensores.py
│   ├── bridge_notificaciones.py
│   ├── composite_activos.py
│   ├── decorator_ordenes.py
│   ├── patron_proxy_flyweight_ml.py   # Patrones Proxy & Flyweight + ML
│   └── facade_cmms.py                 # Patrón Facade
│
├── templates/
│   └── informes.html                  # Dashboard de Telemetría y Chart.js
│
├── conexion.py                         # Patrón Singleton
├── patron_factory.py                   # Patrón Factory Method
├── app.py                              # Archivo principal de rutas (Flask)
├── requirements.txt                    # Dependencias del proyecto
└── README.md
