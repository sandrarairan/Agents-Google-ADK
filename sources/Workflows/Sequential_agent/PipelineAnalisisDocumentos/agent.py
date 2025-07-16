# Part of agent.py --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools import google_search
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
GEMINI_MODEL ="gemini-2.0-flash"

# --- 1. Define Sub-Agents for Each Pipeline Stage ---

# ExtractorAgent
# Takes the initial specification (from user query) and writes code.
extractor_agent = LlmAgent(
    name="ExtractorAgent",
    model=GEMINI_MODEL,
    # Herramienta de búsqueda
    # Change 3: Improved instruction
    instruction="""Eres un Especialista en Extracción de Información de Documentos.
Basándote *únicamente* en el documento proporcionado por el usuario, extrae la información más importante y relevante.

**Tu tarea:**
1. Identifica los puntos clave, datos importantes, fechas, nombres, cifras, y conceptos principales
2. Organiza la información extraída de manera clara y estructurada
3. Mantén la objetividad y no agregues interpretaciones personales

**Formato de salida:**
Presenta la información extraída en categorías claras como:
- Información General
- Datos Numéricos/Estadísticas  
- Personas/Entidades Mencionadas
- Fechas Importantes
- Puntos Clave del Contenido

Proporciona *solo* la información extraída de forma organizada, sin comentarios adicionales.""",
    description="Extrae información clave y datos importantes de documentos.",
    output_key="informacion_extraida" # Almacena salida en state['informacion_extraida']
)

# Agente Analizador de Contenido
# Toma la información extraída por el agente anterior y proporciona análisis profundo.
analizador_agent = LlmAgent(
    name="AnalizadorAgent",
    model=GEMINI_MODEL,
    # Change 3: Improved instruction, correctly using state key injection
    instruction="""Eres un Analista Experto de Contenido.
Tu tarea es analizar profundamente la información extraída y generar insights valiosos.

**Información a Analizar:**
{informacion_extraida}

**Criterios de Análisis:**
1. **Tendencias y Patrones:** ¿Qué tendencias o patrones emergen de los datos?
2. **Implicaciones:** ¿Cuáles son las implicaciones más importantes de esta información?
3. **Relaciones:** ¿Cómo se relacionan entre sí los diferentes elementos?
4. **Oportunidades:** ¿Qué oportunidades o riesgos se pueden identificar?
5. **Context:** ¿Qué significa esta información en el contexto más amplio?

**Salida:**
Proporciona un análisis estructurado con insights claros y accionables.
Enfócate en los hallazgos más significativos que agreguen valor al documento original.
Presenta *solo* el análisis sin comentarios adicionales.""",
    description="Analiza información extraída para generar insights valiosos.",
    output_key="analisis_insights" # Almacena salida en state['analisis_insights']
)


# Agente Creador de Posts para LinkedIn
# Toma la información extraída y el análisis para crear posts atractivos para LinkedIn.
creador_linkedin_agent = LlmAgent(
    name="CreadorLinkedInAgent",
    model=GEMINI_MODEL,
    # Change 3: Improved instruction, correctly using state key injection
    instruction="""Eres un Especialista en Marketing de Contenido para LinkedIn.
Tu objetivo es crear posts atractivos y profesionales para LinkedIn basados en la información y análisis proporcionados.

**Información Extraída:**
{informacion_extraida}

**Análisis e Insights:**
{analisis_insights}

**Tarea:**
Crea un post para LinkedIn que sea:
1. **Atractivo:** Que capture la atención desde las primeras líneas
2. **Profesional:** Mantén un tono apropiado para la red profesional
3. **Valioso:** Que aporte insights útiles a la audiencia
4. **Accionable:** Que incluya llamadas a la acción relevantes
5. **Engaging:** Que fomente la interacción y comentarios

**Estructura del Post:**
- Hook inicial impactante (1-2 líneas)
- Desarrollo del insight principal (3-4 párrafos cortos)
- 3-5 puntos clave con emojis apropiados
- Llamada a la acción final
- Hashtags relevantes (5-8 hashtags)

**Estilo:**
- Usa párrafos cortos para facilitar lectura
- Incluye emojis estratégicamente
- Mantén un tono conversacional pero profesional
- Longitud ideal: 200-300 palabras

**Salida:**
Proporciona *únicamente* el post final listo para publicar en LinkedIn.""",
    description="Crea posts atractivos para LinkedIn basados en extracción y análisis de documentos.",
    output_key="post_linkedin" # Almacena salida en state['post_linkedin']
)


# --- 2. Create the SequentialAgent ---
# This agent orchestrates the pipeline by running the sub_agents in order.
code_pipeline_agent = SequentialAgent(
    name="PipelineAnalisisDocumentos",
    sub_agents=[extractor_agent, analizador_agent, creador_linkedin_agent],
    description="Ejecuta una secuencia de extracción, análisis y creación de posts para LinkedIn basados en documentos.",
    # # Los agentes se ejecutarán en el orden proporcionado: Extractor -> Analizador -> Creador LinkedIn

)

# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = code_pipeline_agent