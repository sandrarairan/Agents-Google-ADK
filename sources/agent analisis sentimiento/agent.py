"""
Agente de Análisis de Sentimientos con Google ADK
Un asistente sofisticado para análisis de sentimientos en español usando Google's Agent Development Kit.
"""

from google.adk.agents import Agent
from google.genai import types
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import re
from collections import Counter

# -------------------------
# Configuración
# -------------------------

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------------------------
# Modelos de Datos
# -------------------------

@dataclass
class AnalisisResultado:
    """Resultado del análisis de sentimientos."""
    texto_original: str
    sentimiento: str  # "positivo", "negativo", "neutral"
    confianza: float  # 0.0 - 1.0
    palabras_clave: List[str]
    puntuacion: float  # -1.0 a 1.0
    estadisticas: Dict[str, int]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class HistorialAnalisis:
    """Historial de análisis realizados."""
    analisis: List[AnalisisResultado] = field(default_factory=list)
    
    def agregar(self, resultado: AnalisisResultado):
        """Agrega un nuevo análisis al historial."""
        self.analisis.append(resultado)
    
    def obtener_estadisticas_globales(self) -> Dict[str, any]:
        """Obtiene estadísticas del historial completo."""
        if not self.analisis:
            return {"total": 0}
        
        sentimientos = [a.sentimiento for a in self.analisis]
        confianzas = [a.confianza for a in self.analisis]
        
        return {
            "total_analisis": len(self.analisis),
            "distribucion_sentimientos": dict(Counter(sentimientos)),
            "confianza_promedio": sum(confianzas) / len(confianzas),
            "ultimo_analisis": self.analisis[-1].timestamp.isoformat()
        }

# -------------------------
# Diccionarios de Palabras
# -------------------------

PALABRAS_POSITIVAS = {
    # Emociones positivas básicas
    "excelente", "genial", "fantástico", "maravilloso", "increíble", "espectacular",
    "bueno", "buena", "buenos", "buenas", "mejor", "mejores", "óptimo", "perfecta", "perfecto",
    "feliz", "alegre", "contento", "contenta", "satisfecho", "satisfecha", "encantado", "encantada",
    
    # Calidad y aprobación
    "calidad", "premium", "superior", "destacado", "destacada", "recomendable", "recomendado",
    "útil", "eficaz", "eficiente", "efectivo", "exitoso", "exitosa", "logrado", "conseguido",
    
    # Experiencias positivas
    "disfrutar", "disfruté", "gozar", "gocé", "amor", "amar", "adoro", "adorar", "encantar",
    "impresionante", "sorprendente", "emocionante", "divertido", "divertida", "entretenido",
    
    # Resultados positivos
    "éxito", "triunfo", "victoria", "ganar", "ganador", "ganadora", "beneficio", "ventaja",
    "progreso", "avance", "mejora", "crecimiento", "desarrollo", "innovación", "creativo",
    
    # Intensificadores positivos
    "muy", "súper", "ultra", "mega", "tremendamente", "extraordinariamente", "absolutamente",
    "definitivamente", "totalmente", "completamente", "realmente", "verdaderamente"
}

PALABRAS_NEGATIVAS = {
    # Emociones negativas básicas
    "malo", "mala", "malos", "malas", "pésimo", "pésima", "terrible", "horrible", "awful",
    "triste", "deprimido", "deprimida", "molesto", "molesta", "enojado", "enojada", "furioso",
    "preocupado", "preocupada", "ansioso", "ansiosa", "estresado", "estresada", "frustrado",
    
    # Problemas y defectos
    "problema", "problemas", "error", "errores", "falla", "fallas", "defecto", "defectos",
    "bug", "bugs", "roto", "rota", "dañado", "dañada", "inútil", "inservible", "deficiente",
    
    # Experiencias negativas  
    "odiar", "odio", "detestar", "detesto", "aborrecer", "disgustar", "molestar", "fastidiar",
    "decepcionar", "decepción", "fracaso", "fracasar", "perder", "pérdida", "fallar", "fallo",
    
    # Calidad negativa
    "barato", "barata", "inferior", "mediocre", "pobre", "lento", "lenta", "confuso", "confusa",
    "complicado", "complicada", "difícil", "imposible", "inadecuado", "inadecuada", "insuficiente",
    
    # Intensificadores negativos
    "nunca", "jamás", "nada", "ningún", "ninguna", "sin", "falta", "faltan", "carece", "carencia",
    "no", "ni", "tampoco", "apenas", "mal", "peor", "pésimamente", "terriblemente"
}

PALABRAS_NEUTRALES = {
    "es", "está", "son", "están", "fue", "será", "tiene", "tener", "hacer", "dice", "dijo",
    "puede", "podría", "tal", "vez", "quizás", "quizá", "posible", "posiblemente", "normal",
    "regular", "común", "típico", "típica", "estándar", "promedio", "medio", "media"
}

MODIFICADORES = {
    # Intensificadores
    "muy": 1.5, "súper": 1.8, "ultra": 1.8, "mega": 1.7, "extremadamente": 2.0,
    "tremendamente": 1.9, "increíblemente": 1.8, "absolutamente": 1.7, "totalmente": 1.6,
    
    # Atenuadores
    "un poco": 0.5, "algo": 0.6, "ligeramente": 0.4, "apenas": 0.3, "casi": 0.7,
    "medio": 0.6, "relativamente": 0.8, "bastante": 1.2, "más o menos": 0.7,
    
    # Negadores
    "no": -1.0, "nunca": -1.2, "jamás": -1.2, "nada": -1.1, "sin": -0.8
}

# -------------------------
# Estado Global
# -------------------------

historial = HistorialAnalisis()

# -------------------------
# Funciones Auxiliares
# -------------------------

def limpiar_texto(texto: str) -> str:
    """Limpia y normaliza el texto para análisis."""
    # Convertir a minúsculas
    texto = texto.lower().strip()
    
    # Remover caracteres especiales pero mantener tildes y ñ
    texto = re.sub(r'[^\w\sáéíóúüñ]', ' ', texto)
    
    # Normalizar espacios
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto

def obtener_palabras(texto: str) -> List[str]:
    """Extrae palabras individuales del texto."""
    texto_limpio = limpiar_texto(texto)
    return [palabra for palabra in texto_limpio.split() if len(palabra) > 2]

def calcular_puntuacion_base(palabras: List[str]) -> Tuple[float, List[str], Dict[str, int]]:
    """Calcula la puntuación base de sentimiento."""
    puntuacion = 0.0
    palabras_encontradas = []
    estadisticas = {"positivas": 0, "negativas": 0, "neutrales": 0, "total": len(palabras)}
    
    for palabra in palabras:
        if palabra in PALABRAS_POSITIVAS:
            puntuacion += 1.0
            palabras_encontradas.append(f"+{palabra}")
            estadisticas["positivas"] += 1
        elif palabra in PALABRAS_NEGATIVAS:
            puntuacion -= 1.0
            palabras_encontradas.append(f"-{palabra}")
            estadisticas["negativas"] += 1
        elif palabra in PALABRAS_NEUTRALES:
            estadisticas["neutrales"] += 1
    
    return puntuacion, palabras_encontradas, estadisticas

def aplicar_modificadores(texto: str, puntuacion_base: float) -> float:
    """Aplica modificadores (intensificadores, negadores) a la puntuación."""
    palabras = obtener_palabras(texto)
    puntuacion_final = puntuacion_base
    
    # Buscar modificadores y aplicarlos
    for i, palabra in enumerate(palabras):
        if palabra in MODIFICADORES:
            modificador = MODIFICADORES[palabra]
            
            # Aplicar modificador a la puntuación base
            if modificador < 0:  # Negador
                puntuacion_final *= modificador
            else:  # Intensificador o atenuador
                puntuacion_final *= modificador
    
    return puntuacion_final

def determinar_sentimiento_y_confianza(puntuacion: float, total_palabras: int) -> Tuple[str, float]:
    """Determina el sentimiento y calcula la confianza."""
    # Normalizar puntuación
    if total_palabras > 0:
        puntuacion_normalizada = puntuacion / total_palabras
    else:
        puntuacion_normalizada = 0.0
    
    # Determinar sentimiento
    if puntuacion_normalizada > 0.1:
        sentimiento = "positivo"
    elif puntuacion_normalizada < -0.1:
        sentimiento = "negativo"
    else:
        sentimiento = "neutral"
    
    # Calcular confianza basada en la magnitud de la puntuación
    confianza = min(abs(puntuacion_normalizada) * 2, 1.0)
    
    # Ajustar confianza basada en cantidad de palabras relevantes
    if total_palabras < 5:
        confianza *= 0.7  # Menos confianza con poco texto
    elif total_palabras > 20:
        confianza = min(confianza * 1.2, 1.0)  # Más confianza con más texto
    
    return sentimiento, confianza

# -------------------------
# Herramientas del Agente
# -------------------------

def analizar_sentimiento(texto: str) -> Dict[str, any]:
    """
    Analiza el sentimiento de un texto en español usando análisis léxico.
    
    Args:
        texto: Texto a analizar
        
    Returns:
        Diccionario con:
        - sentimiento: "positivo", "negativo" o "neutral"
        - confianza: float entre 0 y 1
        - palabras_clave: lista de palabras que indican el sentimiento
        - puntuacion: puntuación numérica (-1.0 a 1.0)
        - estadisticas: contador de tipos de palabras
    """
    logger.info(f"🔍 Analizando sentimiento del texto: '{texto[:50]}...'")
    
    if not texto or not texto.strip():
        return {
            "status": "error",
            "message": "❌ El texto no puede estar vacío."
        }
    
    # Procesar texto
    palabras = obtener_palabras(texto)
    
    if not palabras:
        return {
            "status": "error",
            "message": "❌ No se encontraron palabras válidas en el texto."
        }
    
    # Calcular puntuación base
    puntuacion_base, palabras_clave, estadisticas = calcular_puntuacion_base(palabras)
    
    # Aplicar modificadores
    puntuacion_final = aplicar_modificadores(texto, puntuacion_base)
    
    # Determinar sentimiento y confianza
    sentimiento, confianza = determiner_sentimiento_y_confianza(puntuacion_final, len(palabras))
    
    # Crear resultado
    resultado = AnalisisResultado(
        texto_original=texto,
        sentimiento=sentimiento,
        confianza=confianza,
        palabras_clave=palabras_clave,
        puntuacion=puntuacion_final / len(palabras) if len(palabras) > 0 else 0,
        estadisticas=estadisticas
    )
    
    # Agregar al historial
    historial.agregar(resultado)
    
    # Preparar respuesta
    emoji_sentimiento = {"positivo": "😊", "negativo": "😞", "neutral": "😐"}
    
    return {
        "status": "success",
        "sentimiento": sentimiento,
        "emoji": emoji_sentimiento[sentimiento],
        "confianza": round(confianza, 3),
        "confianza_porcentaje": f"{round(confianza * 100, 1)}%",
        "puntuacion": round(resultado.puntuacion, 3),
        "palabras_clave": palabras_clave,
        "estadisticas": {
            "total_palabras": estadisticas["total"],
            "palabras_positivas": estadisticas["positivas"],
            "palabras_negativas": estadisticas["negativas"],
            "palabras_neutrales": estadisticas["neutrales"]
        },
        "interpretacion": generar_interpretacion(sentimiento, confianza, estadisticas),
        "texto_analizado": texto[:100] + "..." if len(texto) > 100 else texto
    }

def analizar_texto_multiple(textos: List[str]) -> Dict[str, any]:
    """
    Analiza múltiples textos y proporciona estadísticas comparativas.
    
    Args:
        textos: Lista de textos a analizar
        
    Returns:
        Análisis individual y estadísticas comparativas
    """
    logger.info(f"📊 Analizando {len(textos)} textos")
    
    if not textos or len(textos) == 0:
        return {
            "status": "error",
            "message": "❌ Debe proporcionar al menos un texto."
        }
    
    resultados = []
    sentimientos = []
    confianzas = []
    
    for i, texto in enumerate(textos):
        if texto.strip():
            resultado = analizar_sentimiento(texto)
            if resultado["status"] == "success":
                resultados.append({
                    "indice": i + 1,
                    "texto": texto[:50] + "..." if len(texto) > 50 else texto,
                    "sentimiento": resultado["sentimiento"],
                    "confianza": resultado["confianza"],
                    "emoji": resultado["emoji"]
                })
                sentimientos.append(resultado["sentimiento"])
                confianzas.append(resultado["confianza"])
    
    if not resultados:
        return {
            "status": "error",
            "message": "❌ No se pudieron analizar los textos proporcionados."
        }
    
    # Estadísticas comparativas
    distribucion = Counter(sentimientos)
    confianza_promedio = sum(confianzas) / len(confianzas)
    
    return {
        "status": "success",
        "total_textos": len(textos),
        "textos_analizados": len(resultados),
        "resultados_individuales": resultados,
        "estadisticas_globales": {
            "distribucion_sentimientos": dict(distribucion),
            "sentimiento_predominante": distribucion.most_common(1)[0][0],
            "confianza_promedio": round(confianza_promedio, 3),
            "confianza_promedio_porcentaje": f"{round(confianza_promedio * 100, 1)}%"
        },
        "resumen": generar_resumen_multiple(distribucion, confianza_promedio)
    }

def obtener_historial_analisis(limite: Optional[int] = 10) -> Dict[str, any]:
    """
    Obtiene el historial de análisis realizados.
    
    Args:
        limite: Número máximo de análisis a mostrar
        
    Returns:
        Historial de análisis con estadísticas
    """
    logger.info(f"📈 Obteniendo historial (límite: {limite})")
    
    if not historial.analisis:
        return {
            "status": "empty",
            "message": "📝 No hay análisis en el historial.",
            "sugerencia": "Realiza algunos análisis de sentimientos para ver el historial."
        }
    
    # Obtener análisis recientes
    analisis_recientes = historial.analisis[-limite:] if limite else historial.analisis
    
    resultados_historial = []
    for i, analisis in enumerate(reversed(analisis_recientes), 1):
        resultados_historial.append({
            "orden": i,
            "texto": analisis.texto_original[:60] + "..." if len(analisis.texto_original) > 60 else analisis.texto_original,
            "sentimiento": analisis.sentimiento,
            "confianza": f"{round(analisis.confianza * 100, 1)}%",
            "timestamp": analisis.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "palabras_clave": len(analisis.palabras_clave)
        })
    
    estadisticas_globales = historial.obtener_estadisticas_globales()
    
    return {
        "status": "success",
        "historial_reciente": resultados_historial,
        "estadisticas_globales": estadisticas_globales,
        "total_mostrado": len(resultados_historial),
        "mensaje": f"📊 Mostrando {len(resultados_historial)} análisis más recientes"
    }

def limpiar_historial() -> Dict[str, any]:
    """
    Limpia el historial de análisis.
    
    Returns:
        Confirmación de la operación
    """
    logger.info("🧹 Limpiando historial")
    
    total_analisis = len(historial.analisis)
    historial.analisis.clear()
    
    return {
        "status": "success",
        "message": f"🧹 Historial limpiado correctamente.",
        "analisis_eliminados": total_analisis
    }

def analizar_emociones_avanzado(texto: str) -> Dict[str, any]:
    """
    Análisis avanzado que identifica emociones específicas más allá del sentimiento básico.
    
    Args:
        texto: Texto a analizar
        
    Returns:
        Análisis detallado de emociones
    """
    logger.info(f"🎭 Análisis avanzado de emociones")
    
    # Diccionarios de emociones específicas
    emociones = {
        "alegría": ["feliz", "alegre", "contento", "eufórico", "radiante", "jubiloso"],
        "tristeza": ["triste", "deprimido", "melancólico", "desanimado", "abatido"],
        "enojo": ["enojado", "furioso", "iracundo", "molesto", "irritado", "indignado"],
        "miedo": ["miedo", "temor", "pánico", "terror", "asustado", "atemorizado"],
        "sorpresa": ["sorprendido", "asombrado", "impactado", "atónito", "pasmado"],
        "disgusto": ["asco", "repugnancia", "aversión", "disgusto", "náusea"]
    }
    
    palabras = obtener_palabras(texto)
    emociones_detectadas = {}
    
    for emocion, palabras_emocion in emociones.items():
        count = sum(1 for palabra in palabras if palabra in palabras_emocion)
        if count > 0:
            emociones_detectadas[emocion] = count
    
    # Análisis básico también
    analisis_basico = analizar_sentimiento(texto)
    
    if analisis_basico["status"] != "success":
        return analisis_basico
    
    return {
        "status": "success",
        "sentimiento_general": analisis_basico["sentimiento"],
        "confianza_general": analisis_basico["confianza"],
        "emociones_especificas": emociones_detectadas,
        "emocion_predominante": max(emociones_detectadas.items(), key=lambda x: x[1])[0] if emociones_detectadas else "neutral",
        "intensidad_emocional": sum(emociones_detectadas.values()),
        "texto_analizado": texto[:100] + "..." if len(texto) > 100 else texto,
        "palabras_clave_basicas": analisis_basico["palabras_clave"],
        "interpretacion_avanzada": generar_interpretacion_avanzada(emociones_detectadas, analisis_basico["sentimiento"])
    }

# -------------------------
# Funciones de Interpretación
# -------------------------

def generar_interpretacion(sentimiento: str, confianza: float, estadisticas: Dict) -> str:
    """Genera una interpretación legible del análisis."""
    nivel_confianza = "alta" if confianza > 0.7 else "media" if confianza > 0.4 else "baja"
    
    interpretaciones = {
        "positivo": f"El texto expresa un sentimiento positivo con confianza {nivel_confianza} ({round(confianza*100,1)}%). ",
        "negativo": f"El texto expresa un sentimiento negativo con confianza {nivel_confianza} ({round(confianza*100,1)}%). ",
        "neutral": f"El texto tiene un tono neutral con confianza {nivel_confianza} ({round(confianza*100,1)}%). "
    }
    
    base = interpretaciones[sentimiento]
    
    if estadisticas["positivas"] > 0 and estadisticas["negativas"] > 0:
        base += "Se detectaron elementos tanto positivos como negativos en el texto."
    elif estadisticas["total"] < 5:
        base += "El análisis se basa en un texto corto, lo que puede afectar la precisión."
    
    return base

def generar_resumen_multiple(distribucion: Counter, confianza_promedio: float) -> str:
    """Genera un resumen de análisis múltiple."""
    total = sum(distribucion.values())
    predominante = distribucion.most_common(1)[0]
    
    porcentaje = round((predominante[1] / total) * 100, 1)
    nivel_confianza = "alta" if confianza_promedio > 0.7 else "media" if confianza_promedio > 0.4 else "baja"
    
    return f"De {total} textos analizados, {porcentaje}% muestran sentimiento {predominante[0]}. Confianza promedio: {nivel_confianza}."

def generar_interpretacion_avanzada(emociones: Dict, sentimiento_general: str) -> str:
    """Genera interpretación para análisis avanzado de emociones."""
    if not emociones:
        return f"Se detectó un sentimiento {sentimiento_general} sin emociones específicas dominantes."
    
    emocion_principal = max(emociones.items(), key=lambda x: x[1])
    intensidad = sum(emociones.values())
    
    base = f"La emoción predominante es {emocion_principal[0]} (intensidad: {emocion_principal[1]}). "
    
    if len(emociones) > 1:
        base += f"Se detectaron {len(emociones)} tipos de emociones diferentes, indicando complejidad emocional."
    
    if intensidad > 5:
        base += " El texto muestra alta carga emocional."
    
    return base

# Función auxiliar para corregir error de typo
def determiner_sentimiento_y_confianza(puntuacion: float, total_palabras: int) -> Tuple[str, float]:
    """Wrapper para corregir el typo en la función original."""
    return determinar_sentimiento_y_confianza(puntuacion, total_palabras)

# -------------------------
# Configuración del Agente
# -------------------------

root_agent = Agent(
    name="sentiment_analyzer_spanish",
    model="gemini-2.5-flash",
    description="Asistente especializado en análisis de sentimientos para texto en español con capacidades avanzadas de procesamiento emocional.",
    instruction=(
        "Eres un especialista en análisis de sentimientos para textos en español. Tu expertise incluye:\n\n"
        "🎯 CAPACIDADES PRINCIPALES:\n"
        "- Análisis de sentimiento básico (positivo/negativo/neutral)\n"
        "- Análisis avanzado de emociones específicas (alegría, tristeza, enojo, etc.)\n"
        "- Procesamiento de múltiples textos con estadísticas comparativas\n"
        "- Gestión de historial de análisis con tendencias\n"
        "- Interpretación contextual y recomendaciones\n\n"
        "🔍 METODOLOGÍA:\n"
        "- Uso diccionarios léxicos especializados en español\n"
        "- Aplicación de modificadores (intensificadores, negadores)\n"
        "- Cálculo de confianza basado en contexto y longitud\n"
        "- Identificación de palabras clave relevantes\n\n"
        "💡 ESTILO DE COMUNICACIÓN:\n"
        "- Sé preciso pero accesible en tus explicaciones\n"
        "- Usa emojis para hacer los resultados más visuales\n"
        "- Proporciona interpretaciones contextuales útiles\n"
        "- Sugiere mejoras o análisis adicionales cuando sea relevante\n"
        "- Mantén un tono profesional pero amigable\n\n"
        "🚀 PROACTIVIDAD:\n"
        "- Si detectas textos cortos, menciona limitaciones de precisión\n"
        "- Para textos mixtos, explica la complejidad emocional\n"
        "- Sugiere análisis avanzado para casos interesantes\n"
        "- Ofrece insights sobre patrones en análisis múltiples"
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,  # Más determinista para análisis consistente
        max_output_tokens=800,
        top_p=0.8
    ),
    tools=[
        analizar_sentimiento,
        analizar_texto_multiple, 
        obtener_historial_analisis,
        limpiar_historial,
        analizar_emociones_avanzado
    ],
)