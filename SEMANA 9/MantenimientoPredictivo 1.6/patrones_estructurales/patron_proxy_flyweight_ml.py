# patrones_estructurales/patron_proxy_flyweight_ml.py
import time
import random

# ==========================================
# 1. PATRÓN FLYWEIGHT (Optimización de Memoria)
# ==========================================

class MetadatosSensorFlyweight:
    """
    Estado Intrínseco (Compartido): Atributos fijos y pesados que no cambian
    entre lecturas del mismo tipo de sensor (ej. unidades, umbrales seguros).
    """
    def __init__(self, tipo_variable: str, unidad_medida: str, umbral_maximo: float):
        self.tipo_variable = tipo_variable
        self.unidad_medida = unidad_medida
        self.umbral_maximo = umbral_maximo

class FabricaFlyweightSensores:
    """
    Fábrica Flyweight que asegura reutilizar una única instancia de metadatos
    por cada tipo de variable industrial.
    """
    _flyweights = {}

    @classmethod
    def obtener_flyweight(cls, tipo_variable: str) -> MetadatosSensorFlyweight:
        tipo = (tipo_variable or "General").strip().lower()
        if tipo not in cls._flyweights:
            if "temperatura" in tipo:
                cls._flyweights[tipo] = MetadatosSensorFlyweight("Temperatura", "°C", 85.0)
            elif "vibracion" in tipo or "vibración" in tipo:
                cls._flyweights[tipo] = MetadatosSensorFlyweight("Vibración", "mm/s", 7.5)
            elif "presion" in tipo or "presión" in tipo:
                cls._flyweights[tipo] = MetadatosSensorFlyweight("Presión", "PSI", 120.0)
            elif "corriente" in tipo:
                cls._flyweights[tipo] = MetadatosSensorFlyweight("Corriente", "A", 45.0)
            elif "flujo" in tipo:
                cls._flyweights[tipo] = MetadatosSensorFlyweight("Flujo", "L/min", 200.0)
            else:
                cls._flyweights[tipo] = MetadatosSensorFlyweight("General", "Unidades", 100.0)
        return cls._flyweights[tipo]


class LecturaSensorContexto:
    """
    Estado Extrínseco (Variable): Lectura puntual que combina el Flyweight compartido
    con el valor numérico en un instante específico.
    """
    def __init__(self, sensor_id: int, valor_actual: float, tipo_variable: str):
        self.sensor_id = sensor_id
        self.valor_actual = valor_actual
        self.flyweight = FabricaFlyweightSensores.obtener_flyweight(tipo_variable)

    def calcular_porcentaje_riesgo(self) -> float:
        """Calcula el riesgo relativo según el umbral compartido del Flyweight."""
        if self.flyweight.umbral_maximo == 0:
            return 0.0
        return round((self.valor_actual / self.flyweight.umbral_maximo) * 100, 2)


# ==========================================
# 2. MOTOR REAL DE MACHINE LEARNING (Sujeto)
# ==========================================

class ModeloPredictivoMLReal:
    """
    Simulación del Modelo pesado de ML / Detección de Anomalías.
    Su inicialización y ejecución consumen recursos.
    """
    def __init__(self):
        print("🧠 [ML Motor] Cargando pesos del modelo de IA en memoria RAM... (Operación Pesada)")
        time.sleep(0.3)
        self.modelo_cargado = True

    def predecir_falla(self, lecturas_flyweight: list) -> dict:
        """Evalúa un conjunto de lecturas optimizadas con Flyweight."""
        if not lecturas_flyweight:
            return {
                "estado_predictivo": "Sin Datos de Telemetría",
                "probabilidad_falla": 0.0,
                "nivel_alerta": "Baja",
                "tiempo_estimado_falla_horas": 720
            }

        riesgo_promedio = sum(l.calcular_porcentaje_riesgo() for l in lecturas_flyweight) / len(lecturas_flyweight)
        
        probabilidad = min(round(riesgo_promedio * 0.85 + random.uniform(1, 5), 1), 99.9)
        
        if probabilidad >= 75.0:
            estado_predictivo = "Peligro Inminente / Falla Detectada"
            alerta = "Alta"
        elif probabilidad >= 50.0:
            estado_predictivo = "Advertencia / Desgaste Detectado"
            alerta = "Media"
        else:
            estado_predictivo = "Operación Normal / Estable"
            alerta = "Baja"

        return {
            "estado_predictivo": estado_predictivo,
            "probabilidad_falla": probabilidad,
            "nivel_alerta": alerta,
            "tiempo_estimado_falla_horas": round(100 - probabilidad, 1) if probabilidad > 50 else 720
        }


# ==========================================
# 3. PATRÓN PROXY (Lazy Loading y Caching)
# ==========================================

class ProxyModeloPredictivo:
    """
    Proxy que controla el acceso al modelo pesado de ML:
    - Lazy Loading: No instancia el objeto real hasta que se requiere.
    - Caching: Almacena en memoria temporal las predicciones recientes.
    """
    def __init__(self):
        self._modelo_real = None
        self._cache_predicciones = {}
        self._tiempo_vida_cache = 300  # 5 minutos de caché

    def _obtener_instancia_modelo(self) -> ModeloPredictivoMLReal:
        if self._modelo_real is None:
            self._modelo_real = ModeloPredictivoMLReal()
        return self._modelo_real

    def predecir_falla_equipo(self, nombre_equipo: str, lecturas_raw: list) -> dict:
        tiempo_actual = time.time()

        # Verificar respuesta guardada en caché
        if nombre_equipo in self._cache_predicciones:
            item_cache = self._cache_predicciones[nombre_equipo]
            if tiempo_actual - item_cache["timestamp"] < self._tiempo_vida_cache:
                print(f"⚡ [PROXY] Devolviendo predicción desde CACHÉ para: {nombre_equipo}")
                resultado = item_cache["resultado"].copy()
                resultado["origen"] = "Proxy Cache (Rápido)"
                return resultado

        print(f"🔍 [PROXY] Ejecutando análisis ML en tiempo real para: {nombre_equipo}")

        # Creación de instancias con Flyweight
        lecturas_flyweight = [
            LecturaSensorContexto(r.get("id", 0), float(r.get("valor", 0)), r.get("tipo", "General"))
            for r in lecturas_raw
        ]

        # Invocación con Lazy Loading
        modelo = self._obtener_instancia_modelo()
        resultado = modelo.predecir_falla(lecturas_flyweight)
        resultado["origen"] = "Modelo ML Real (Calculado)"

        # Guardar resultado en caché
        self._cache_predicciones[nombre_equipo] = {
            "timestamp": tiempo_actual,
            "resultado": resultado
        }

        return resultado

# Instancia global requerida por app.py
proxy_predictivo_global = ProxyModeloPredictivo()