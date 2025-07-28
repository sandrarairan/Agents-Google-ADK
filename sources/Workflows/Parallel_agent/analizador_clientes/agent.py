# Customer Success & Support - Google ADK Workflow
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents import SequentialAgent, ParallelAgent
from google.adk.tools import google_search
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Modelo de Gemini
GEMINI_MODELO = "gemini-2.5-flash"

# --- 1. Definir Sub-Agentes Especialistas (Ejecutión Paralela) ---

# Especialista 1: Analizador de Feedback de Clientes
analizador_feedback = LlmAgent(
    name="AnalizadorFeedbackClientes",
    model=GEMINI_MODELO,
    instruction="""Eres un especialista en análisis de feedback y sentiment de clientes.

Tu tarea es investigar y analizar el feedback de clientes para la empresa/producto especificado por el usuario.

Busca información sobre:
- Reviews y ratings en plataformas relevantes (Google, Trustpilot, G2, Capterra, etc.)
- Comentarios en redes sociales
- Quejas comunes y patrones de insatisfacción
- Aspectos más valorados por los clientes
- Sentiment general y tendencias temporales

Usa la herramienta de Búsqueda de Google proporcionada.

Resume tus hallazgos clave de forma concisa, incluyendo:
- Sentiment score general (positivo/negativo/neutro)
- Top 3 quejas más frecuentes
- Top 3 aspectos más valorados
- Patrones temporales (mejora/empeoramiento)

Tu salida debe ser *únicamente* el resumen estructurado.
""",
    description="Analiza feedback y sentiment de clientes.",
    tools=[google_search],
    output_key="resultado_feedback"
)

# Especialista 2: Investigador de Patrones de Churn
investigador_churn = LlmAgent(
    name="InvestigadorPatronesChurn",
    model=GEMINI_MODELO,
    instruction="""Eres un especialista en análisis de churn y retención de clientes.

Tu tarea es investigar patrones de cancelación y abandono para la empresa/sector especificado por el usuario.

Busca información sobre:
- Tasas de churn típicas en la industria
- Principales razones de cancelación reportadas
- Momentos críticos en el customer journey donde ocurre más churn
- Señales tempranas de riesgo de churn
- Estrategias exitosas de retención en empresas similares

Usa la herramienta de Búsqueda de Google proporcionada.

Resume tus hallazgos clave de forma concisa, incluyendo:
- Benchmarks de churn de la industria
- Top 5 razones principales de churn
- Momentos de mayor riesgo en el customer journey
- Señales de alerta temprana
- 3 estrategias de retención más efectivas

Tu salida debe ser *únicamente* el resumen estructurado.
""",
    description="Investiga patrones de churn y estrategias de retención.",
    tools=[google_search],
    output_key="resultado_churn"
)

# Especialista 3: Especialista en Oportunidades de Upselling
especialista_upselling = LlmAgent(
    name="EspecialistaUpsellingOportunidades",
    model=GEMINI_MODELO,
    instruction="""Eres un especialista en identificación de oportunidades de crecimiento y upselling.

Tu tarea es investigar oportunidades de expansión de ingresos con clientes existentes para la empresa/sector especificado.

Busca información sobre:
- Estrategias de upselling exitosas en la industria
- Productos/servicios complementarios más demandados
- Timing óptimo para propuestas de upselling
- Segmentos de clientes con mayor propensión a expandir
- Métricas clave de expansion revenue

Usa la herramienta de Búsqueda de Google proporcionada.

Resume tus hallazgos clave de forma concisa, incluyendo:
- Top 3 oportunidades de upselling más efectivas
- Timing recomendado para cada tipo de propuesta
- Segmentos de clientes más propensos al upselling
- Mensajes/approaches más exitosos
- Métricas de referencia de expansion revenue

Tu salida debe ser *únicamente* el resumen estructurado.
""",
    description="Identifica oportunidades de upselling y expansion revenue.",
    tools=[google_search],
    output_key="resultado_upselling"
)

# Especialista 4: Evaluador de Métricas de Satisfacción
evaluador_satisfaction = LlmAgent(
    name="EvaluadorSatisfactionMetrics",
    model=GEMINI_MODELO,
    instruction="""Eres un especialista en métricas de satisfacción y experiencia del cliente.

Tu tarea es investigar KPIs y benchmarks de satisfacción del cliente para la empresa/sector especificado.

Busca información sobre:
- KPIs estándar de Customer Success (NPS, CSAT, CES, etc.)
- Benchmarks de la industria para métricas clave
- Herramientas y metodologías de medición más efectivas
- Correlación entre métricas y business outcomes
- Best practices en Customer Success teams

Usa la herramienta de Búsqueda de Google proporcionada.

Resume tus hallazgos clave de forma concisa, incluyendo:
- Benchmarks de NPS, CSAT, CES para la industria
- Top 3 KPIs más predictivos de retención
- Herramientas recomendadas para tracking
- Frecuencia óptima de medición
- Correlaciones clave con revenue/retention

Tu salida debe ser *únicamente* el resumen estructurado.
""",
    description="Evalúa métricas de satisfacción y benchmarks de industria.",
    tools=[google_search],
    output_key="resultado_satisfaction"
)

# --- 2. Crear el ParallelAgent ---
agente_investigacion_customer_success = ParallelAgent(
    name="AgenteInvestigacionCustomerSuccessParalelo",
    sub_agents=[analizador_feedback, investigador_churn, especialista_upselling, evaluador_satisfaction],
    description="Ejecuta múltiples análisis de Customer Success en paralelo."
)

# --- 3. Definir el Agente Sintetizador ---
customer_success_strategist = LlmAgent(
    name="CustomerSuccessStrategist",
    model=GEMINI_MODELO,
    instruction="""Eres un Customer Success Strategist senior con experiencia en empresas SaaS y de servicios.

Tu tarea es combinar los siguientes análisis especializados en una estrategia integral de Customer Success.

**IMPORTANTE: Tu respuesta DEBE basarse *exclusivamente* en la información proporcionada en los análisis de entrada. NO añadas conocimiento externo.**

**Análisis de Entrada:**

* **Análisis de Feedback:**
    {resultado_feedback}

* **Patrones de Churn:**
    {resultado_churn}

* **Oportunidades de Upselling:**
    {resultado_upselling}

* **Métricas de Satisfacción:**
    {resultado_satisfaction}

**Formato de Salida:**

# Estrategia Integral de Customer Success

## 🎯 Executive Summary
[Resumen ejecutivo basado en los hallazgos principales]

## 📊 Situación Actual del Cliente
### Análisis de Sentiment y Feedback
[Sintetiza únicamente los hallazgos del análisis de feedback]

### Riesgos de Churn Identificados
[Detalla únicamente los patrones de churn encontrados]

## 🚀 Oportunidades de Crecimiento
### Expansion Revenue Opportunities
[Basado únicamente en el análisis de upselling]

### Benchmarks y KPIs Objetivo
[Basado únicamente en las métricas de satisfacción investigadas]

## 📋 Plan de Acción Prioritizado
### Iniciativas de Retención (Corto Plazo - 0-3 meses)
[Acciones basadas en los riesgos de churn identificados]

### Estrategias de Expansión (Mediano Plazo - 3-6 meses)
[Iniciativas basadas en las oportunidades de upselling]

### Optimización de Métricas (Largo Plazo - 6-12 meses)
[Plan basado en los benchmarks y KPIs investigados]

## 🎯 Recomendaciones Específicas
### Para Reducir Churn
[Recomendaciones específicas basadas en los patrones identificados]

### Para Mejorar Satisfaction
[Acciones basadas en el análisis de feedback]

### Para Incrementar Expansion Revenue
[Estrategias específicas basadas en las oportunidades identificadas]

## 📈 KPIs y Métricas de Seguimiento
[Lista de métricas clave basada en el análisis de satisfaction]

## 🎯 Next Steps Inmediatos
[3-5 acciones prioritarias basadas en todos los análisis]

Tu salida debe ser *únicamente* el plan estratégico siguiendo esta estructura exacta.
""",
    description="Sintetiza los análisis en una estrategia integral de Customer Success.",
)

# --- 4. Crear el SequentialAgent Principal ---
pipeline_customer_success = SequentialAgent(
    name="PipelineCustomerSuccessCompleto",
    sub_agents=[agente_investigacion_customer_success, customer_success_strategist],
    description="Coordina el análisis paralelo de Customer Success y sintetiza la estrategia final."
)

# --- 5. Agente raíz para ejecutar todo el workflow ---
# IMPORTANTE: Esta variable debe estar al nivel del módulo para ser encontrada por Google ADK
root_agent = pipeline_customer_success