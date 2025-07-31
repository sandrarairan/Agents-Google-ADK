# Part of agent.py --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup

import asyncio
import os
from google.adk.agents import LoopAgent, LlmAgent, BaseAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools.tool_context import ToolContext

# --- Constants ---
GEMINI_MODEL = "gemini-2.0-flash"
# Supply Chain Optimization Agent

# Herramienta para finalizar optimización
def finalize_supply_plan(tool_context: ToolContext):
    """Call this function ONLY when the supply chain optimization is complete and no further adjustments are needed."""
    print(f"  [Tool Call] finalize_supply_plan triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {}

# Herramienta para escalar riesgos críticos
def escalate_critical_risk(tool_context: ToolContext):
    """Call this function when critical supply chain risks are identified that require immediate human intervention."""
    print(f"  [Tool Call] escalate_critical_risk triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {"status": "critical_risk_escalated", "requires_human_intervention": True}

print("\n=== Supply Chain Optimization Agent ===")

# Agente predictor de demanda
demand_forecaster = LlmAgent(
    name="DemandForecaster",
    model="gemini-2.0-flash",
    instruction=(
        "Analiza los datos históricos de demanda, tendencias de mercado, estacionalidad y eventos especiales "
        "para generar una predicción precisa de demanda. "
        "Considera factores como: "
        "- Datos históricos de ventas "
        "- Tendencias estacionales "
        "- Eventos promocionales planificados "
        "- Factores económicos externos "
        "- Lanzamientos de productos "
        "Proporciona predicciones por producto, región y período de tiempo con intervalos de confianza."
    ),
    output_key="demand_forecast"
)

# Agente planificador de suministros
supply_planner = LlmAgent(
    name="SupplyPlanner",
    model="gemini-2.0-flash",
    instruction=(
        "Basándote en la predicción de demanda 'demand_forecast', crea un plan de suministros óptimo que incluya: "
        "- Selección de proveedores y evaluación de capacidad "
        "- Niveles de inventario óptimos por producto y ubicación "
        "- Cronograma de pedidos y entregas "
        "- Estrategias de sourcing (único vs múltiples proveedores) "
        "- Costos totales de suministro y almacenamiento "
        "- Tiempos de lead time y buffers de seguridad "
        "Optimiza para minimizar costos mientras aseguras disponibilidad."
    ),
    output_key="supply_plan"
)

# Agente mitigador de riesgos
risk_mitigator = LlmAgent(
    name="RiskMitigator",
    model="gemini-2.5-flash",
    instruction=(
        "Analiza el plan de suministros 'supply_plan' y la predicción 'demand_forecast' para identificar y mitigar riesgos: "
        "TIPOS DE RIESGOS A EVALUAR: "
        "- Riesgos de proveedores (financieros, operacionales, geopolíticos) "
        "- Riesgos de transporte y logística "
        "- Riesgos de inventario (obsolescencia, faltantes) "
        "- Riesgos de demanda (variabilidad, cambios súbitos) "
        "- Riesgos externos (desastres naturales, regulatorios) "
        ""
        "CRITERIOS DE FINALIZACIÓN: "
        "Si el plan tiene riesgos CRÍTICOS (probabilidad alta + impacto alto), llama a escalate_critical_risk. "
        "Si todos los riesgos están mitigados adecuadamente y el plan es robusto, di exactamente: "
        "'Plan de supply chain optimizado y riesgos mitigados satisfactoriamente.' y llama a finalize_supply_plan. "
        "De lo contrario, proporciona recomendaciones específicas para mejorar la mitigación de riesgos."
    ),
    tools=[finalize_supply_plan, escalate_critical_risk],
    output_key="risk_assessment"
)

# Loop de optimización de supply chain
loop_supply_chain = LoopAgent(
    name="LoopSupplyChain",
    sub_agents=[demand_forecaster, supply_planner, risk_mitigator],
    max_iterations=5  # Máximo 5 iteraciones para optimización
)

root_agent = loop_supply_chain