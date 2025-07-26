# Part of agent.py --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools import google_search
import smtplib
import uuid
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
import json
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()

GEMINI_MODEL = "gemini-2.0-flash"

# Gmail configuration
GMAIL_USER = os.getenv("GMAIL_USER")  # tu_email@gmail.com
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # App password de Gmail
APPROVER_EMAIL = os.getenv("APPROVER_EMAIL")  # email del aprobador

# --- Custom Tool Functions ---

def send_approval_email(expense_amount: str, expense_category: str, expense_description: str, 
                       expense_date: str, employee_name: str, validation_message: str) -> Dict[str, Any]:
    """
    Envía email de aprobación con botones.
    
    Args:
        expense_amount: Monto del gasto
        expense_category: Categoría del gasto
        expense_description: Descripción del gasto
        expense_date: Fecha del gasto
        employee_name: Nombre del empleado
        validation_message: Mensaje de validación de políticas
        
    Returns:
        Dict con status, transaction_id y mensaje
    """
    try:
        # Verificar configuración de Gmail
        if not GMAIL_USER or not GMAIL_PASSWORD or not APPROVER_EMAIL:
            error_msg = f"❌ Configuración de Gmail incompleta: USER={bool(GMAIL_USER)}, PASS={bool(GMAIL_PASSWORD)}, APPROVER={bool(APPROVER_EMAIL)}"
            print(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
        
        print(f"📧 Iniciando envío de email de aprobación...")
        print(f"   Monto: ${expense_amount}")
        print(f"   Categoría: {expense_category}")
        print(f"   Empleado: {employee_name}")
        print(f"   Destinatario: {APPROVER_EMAIL}")
        
        # Generar ID único para la transacción
        transaction_id = str(uuid.uuid4())
        
        # Construir expense_data desde parámetros individuales
        expense_data = {
            'amount': expense_amount,
            'category': expense_category,
            'description': expense_description,
            'date': expense_date,
            'employee': employee_name
        }
        
        print(f"📨 Conectando a servidor SMTP de Gmail...")
        
        # Configurar servidor SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        
        print(f"✅ Conexión SMTP exitosa, preparando mensaje...")
        
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['From'] = GMAIL_USER
        msg['To'] = APPROVER_EMAIL
        msg['Subject'] = f"Aprobación de Gasto - {expense_data.get('category', 'General')}"
        
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['From'] = GMAIL_USER
        msg['To'] = APPROVER_EMAIL
        msg['Subject'] = f"Aprobación de Gasto - {expense_data.get('category', 'General')}"
        
        # HTML con botones (usando puerto 8001 para coincidir con webhook_server.py)
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                    Solicitud de Aprobación de Gasto
                </h2>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2980b9; margin-top: 0;">Detalles del Gasto:</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Monto:</td>
                            <td style="padding: 8px;">${expense_data.get('amount', 'N/A')}</td>
                        </tr>
                        <tr style="background-color: #ecf0f1;">
                            <td style="padding: 8px; font-weight: bold;">Categoría:</td>
                            <td style="padding: 8px;">{expense_data.get('category', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Descripción:</td>
                            <td style="padding: 8px;">{expense_data.get('description', 'N/A')}</td>
                        </tr>
                        <tr style="background-color: #ecf0f1;">
                            <td style="padding: 8px; font-weight: bold;">Fecha:</td>
                            <td style="padding: 8px;">{expense_data.get('date', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: bold;">Empleado:</td>
                            <td style="padding: 8px;">{expense_data.get('employee', 'N/A')}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 20px 0;">
                    <h3 style="color: #856404; margin-top: 0;">Validación de Políticas:</h3>
                    <p style="margin: 0;">{validation_message}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="font-size: 16px; margin-bottom: 20px;">
                        <strong>¿Aprueba este gasto?</strong>
                    </p>
                    
                    <a href="http://localhost:8001/approve/{transaction_id}" 
                       style="display: inline-block; background-color: #27ae60; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; margin: 0 10px; font-weight: bold;">
                        ✅ APROBAR
                    </a>
                    
                    <a href="http://localhost:8001/reject/{transaction_id}" 
                       style="display: inline-block; background-color: #e74c3c; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; margin: 0 10px; font-weight: bold;">
                        ❌ RECHAZAR
                    </a>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #bdc3c7; 
                           font-size: 12px; color: #7f8c8d; text-align: center;">
                    <p>Este email fue generado automáticamente por el sistema de procesamiento de gastos.</p>
                    <p>ID de transacción: {transaction_id}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Adjuntar HTML
        msg.attach(MIMEText(html_body, 'html'))
        
        # Enviar email
        print(f"📤 Enviando email...")
        server.sendmail(GMAIL_USER, APPROVER_EMAIL, msg.as_string())
        server.quit()
        
        print(f"✅ Email de aprobación enviado exitosamente!")
        print(f"   Transaction ID: {transaction_id[:8]}...")
        print(f"   Approve URL: http://localhost:8001/approve/{transaction_id}")
        print(f"   Reject URL: http://localhost:8001/reject/{transaction_id}")
        
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "message": "Email de aprobación enviado exitosamente",
            "approve_url": f"http://localhost:8001/approve/{transaction_id}",
            "reject_url": f"http://localhost:8001/reject/{transaction_id}"
        }
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"❌ Error de autenticación SMTP: {str(e)} - Verifica GMAIL_USER y GMAIL_APP_PASSWORD"
        print(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }
    except smtplib.SMTPException as e:
        error_msg = f"❌ Error SMTP: {str(e)}"
        print(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }
    except Exception as e:
        error_msg = f"❌ Error general enviando email: {str(e)}"
        print(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }

def process_approval_response(transaction_id, decision, comments=""):
    """Procesa la respuesta de aprobación del webhook"""
    try:
        # Aquí podrías guardar en base de datos, etc.
        result = {
            "transaction_id": transaction_id,
            "decision": decision,
            "comments": comments,
            "timestamp": "2024-01-01T00:00:00Z"  # En producción usar datetime.now()
        }
        
        # Enviar email de confirmación
        send_confirmation_email(result)
        
        return result
    except Exception as e:
        return {"error": f"Error procesando respuesta: {str(e)}"}

def send_confirmation_email(approval_result):
    """Envía email de confirmación al empleado"""
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        
        decision = approval_result['decision']
        status_color = "#27ae60" if decision == "approved" else "#e74c3c"
        status_text = "APROBADO" if decision == "approved" else "RECHAZADO"
        status_icon = "✅" if decision == "approved" else "❌"
        
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_USER  # En producción, usar email del empleado
        msg['Subject'] = f"Gasto {status_text} - ID: {approval_result['transaction_id'][:8]}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; padding: 20px; background-color: {status_color}; 
                           color: white; border-radius: 8px; margin-bottom: 20px;">
                    <h1 style="margin: 0; font-size: 24px;">
                        {status_icon} Gasto {status_text}
                    </h1>
                </div>
                
                <p>Su solicitud de gasto ha sido <strong>{status_text.lower()}</strong>.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>ID de transacción:</strong> {approval_result['transaction_id']}</p>
                    <p><strong>Fecha de decisión:</strong> {approval_result['timestamp']}</p>
                    {f"<p><strong>Comentarios:</strong> {approval_result.get('comments', 'Sin comentarios')}</p>" if approval_result.get('comments') else ""}
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #bdc3c7; 
                           font-size: 12px; color: #7f8c8d; text-align: center;">
                    <p>Sistema automatizado de procesamiento de gastos</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        server.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())
        server.quit()
        
        return {"status": "success", "message": "Email de confirmación enviado"}
        
    except Exception as e:
        return {"status": "error", "message": f"Error enviando confirmación: {str(e)}"}

# --- 1. Define Sub-Agents for Expense Processing Pipeline ---

# Receipt Digitizer Agent
receipt_digitizer_agent = LlmAgent(
    name="ReceiptDigitizerAgent",
    model=GEMINI_MODEL,
    tools=[google_search],
    instruction="""Eres un agente que digitaliza y extrae información de recibos de gastos.
    
    Analiza la información del gasto proporcionada y extrae:
    - Monto total
    - Fecha del gasto
    - Categoría (comida, transporte, materiales, etc.)
    - Descripción detallada
    - Comercio/proveedor
    - Empleado que realizó el gasto
    
    Devuelve la información en formato JSON estructurado:
    {
        "amount": "cantidad_numerica",
        "date": "YYYY-MM-DD",
        "category": "categoria",
        "description": "descripcion_detallada",
        "merchant": "nombre_comercio",
        "employee": "nombre_empleado"
    }
    
    Si falta información, usa valores por defecto razonables o marca como "N/A".
    """,
    description="Digitaliza recibos y extrae información estructurada",
    output_key="digitized_receipt"
)

# Expense Categorizer Agent
expense_categorizer_agent = LlmAgent(
    name="ExpenseCategorizerAgent",
    model=GEMINI_MODEL,
    instruction="""Eres un experto en categorización de gastos empresariales.
    
    **Recibo digitalizado:**
    {digitized_receipt}
    
    Tu tarea es:
    1. Validar y mejorar la categorización del gasto
    2. Asignar subcategoría específica
    3. Determinar si es un gasto deducible de impuestos
    4. Calcular el monto final con impuestos si aplica
    
    Categorías principales disponibles:
    - Alimentación (comidas de negocio, catering)
    - Transporte (combustible, taxi, vuelos, hotel)
    - Materiales de oficina (papelería, equipos)
    - Tecnología (software, hardware)
    - Marketing (publicidad, eventos)
    - Servicios profesionales (consultoría, legal)
    - Otros gastos operativos
    
    Devuelve en formato JSON:
    {
        "original_data": "copia_del_recibo_original",
        "category": "categoria_principal",
        "subcategory": "subcategoria_especifica",
        "tax_deductible": true/false,
        "final_amount": "monto_final_con_impuestos",
        "categorization_notes": "notas_adicionales"
    }
    """,
    description="Categoriza gastos según políticas empresariales",
    output_key="categorized_expense"
)

# Policy Validator Agent
policy_validator_agent = LlmAgent(
    name="PolicyValidatorAgent", 
    model=GEMINI_MODEL,
    instruction="""Eres un validador de políticas de gastos empresariales.
    
    **Gasto categorizado:**
    {categorized_expense}
    
    Políticas de la empresa a validar:
    1. Gastos de alimentación: máximo $50 por día por empleado
    2. Transporte: requiere justificación de negocio para montos >$100
    3. Materiales de oficina: máximo $200 por mes por empleado
    4. Tecnología: requiere aprobación previa para montos >$500
    5. Todos los gastos requieren recibo válido
    6. Gastos de entretenimiento limitados a $100 por evento
    
    Valida el gasto contra estas políticas y determina:
    - Si cumple con las políticas (APPROVED/NEEDS_APPROVAL/REJECTED)
    - Razones específicas si no cumple
    - Monto aprobado (puede ser menor al solicitado)
    - Documentación adicional requerida
    
    Devuelve en formato JSON:
    {
        "validation_status": "APPROVED/NEEDS_APPROVAL/REJECTED",
        "approved_amount": "monto_aprobado",
        "policy_violations": ["lista_de_violaciones"],
        "required_documentation": ["documentos_adicionales_necesarios"],
        "validation_notes": "notas_del_validador",
        "requires_manager_approval": true/false
    }
    """,
    description="Valida gastos contra políticas empresariales",
    output_key="validation_result"
)

# Approval Email Sender Agent
approval_email_sender_agent = LlmAgent(
    name="ApprovalEmailSenderAgent",
    model=GEMINI_MODEL,
    tools=[send_approval_email],
    instruction="""Eres un agente que gestiona el envío de emails de aprobación.
    
    **Gasto categorizado:**
    {categorized_expense}
    
    **Resultado de validación:**
    {validation_result}
    
    IMPORTANTE: Debes SIEMPRE llamar a la función send_approval_email cuando el gasto necesite aprobación.
    
    Tu tarea es:
    1. Analizar si el gasto necesita aprobación manual
    2. Extraer los datos del gasto categorizado para el email
    3. OBLIGATORIO: Llamar a send_approval_email si se necesita aprobación
    4. Reportar el resultado
    
    REGLAS:
    - Si validation_status es "NEEDS_APPROVAL" o requires_manager_approval es true → DEBES llamar send_approval_email
    - Si validation_status es "APPROVED" → no envíes email, continúa al siguiente paso
    - Si validation_status es "REJECTED" → no envíes email, marca como rechazado
    
    EJEMPLO DE USO DE LA FUNCIÓN:
    Para gastos que necesitan aprobación, debes llamar:
    send_approval_email(
        expense_amount="501",
        expense_category="Tecnología", 
        expense_description="Teclado ergonómico por indicaciones médicas",
        expense_date="2025-04-13",
        employee_name="Usuario",
        validation_message="Gasto de tecnología mayor a $500, requiere aprobación gerencial"
    )
    
    Después de llamar la función (o decidir no llamarla), devuelve el resultado en formato JSON:
    {
        "email_sent": true/false,
        "transaction_id": "id_de_la_funcion_si_se_envio",
        "email_status": "sent/not_needed/error",
        "next_action": "wait_approval/proceed_to_payment/reject",
        "message": "descripcion_de_la_accion",
        "function_result": "resultado_de_send_approval_email_si_se_llamo"
    }
    """,
    description="Envía emails de aprobación a los gerentes",
    output_key="email_result"
)

# Approval Router Agent  
approval_router_agent = LlmAgent(
    name="ApprovalRouterAgent",
    model=GEMINI_MODEL,
    instruction="""Eres un agente que gestiona el enrutamiento de aprobaciones.
    
    **Resultado del email:**
    {email_result}
    
    **Resultado de validación:**
    {validation_result}
    
    Tu tarea es determinar el siguiente paso basado en:
    1. Si se envió email de aprobación
    2. El estado de validación de políticas
    3. Si se requiere aprobación manual
    
    IMPORTANTE: NO llames a ninguna función externa. Solo analiza y decide el routing.
    
    Lógica de routing:
    - Si email_result.email_sent es true → "wait_for_approval" (espera respuesta del gerente)
    - Si validation_result.validation_status es "APPROVED" → "proceed_to_payment"
    - Si validation_result.validation_status es "REJECTED" → "rejected"
    - Si validation_result.requires_manager_approval es false y validation_status es "APPROVED" → "proceed_to_payment"
    
    Devuelve en formato JSON:
    {
        "routing_decision": "wait_for_approval/proceed_to_payment/rejected/requires_documentation",
        "status": "approved/pending/rejected/needs_docs",
        "approved_amount": "monto_final_aprobado",
        "transaction_id": "id_de_transaccion_si_existe",
        "next_steps": ["lista_de_pasos_siguientes"],
        "routing_notes": "explicacion_de_la_decision_tomada",
        "requires_human_action": true/false
    }
    """,
    description="Enruta gastos según necesidades de aprobación",
    output_key="routing_result"
)

# Payment Processor Agent
payment_processor_agent = LlmAgent(
    name="PaymentProcessorAgent",
    model=GEMINI_MODEL,
    instruction="""Eres el agente final que procesa los pagos aprobados.
    
    **Resultado de enrutamiento:**
    {routing_result}
    
    **Gasto original:**
    {categorized_expense}
    
    **Email result:**
    {email_result}
    
    IMPORTANTE: Solo procesa pagos para gastos completamente aprobados.
    
    Lógica de procesamiento:
    - Si routing_decision es "proceed_to_payment" → procesar pago inmediatamente
    - Si routing_decision es "wait_for_approval" → marcar como pendiente de aprobación
    - Si routing_decision es "rejected" → marcar como rechazado
    - Si routing_decision es "requires_documentation" → marcar como necesita documentos
    
    Para gastos que proceden al pago:
    1. Genera un número de referencia de pago
    2. Prepara la información para el sistema de pagos
    3. Registra el gasto en contabilidad
    4. Marca como procesado
    
    Para gastos pendientes de aprobación:
    1. Marca como pendiente
    2. Proporciona información de seguimiento
    3. Incluye URLs de aprobación si existen
    
    Devuelve en formato JSON:
    {
        "payment_processed": true/false,
        "payment_reference": "numero_de_referencia_o_null",
        "processed_amount": "monto_procesado_o_pendiente",
        "processing_date": "fecha_procesamiento_o_null",
        "accounting_entry": "numero_de_asiento_contable_o_null",
        "final_status": "paid/pending_approval/rejected/needs_docs",
        "transaction_id": "id_de_transaccion_si_existe",
        "approval_urls": {
            "approve": "url_de_aprobacion_o_null",
            "reject": "url_de_rechazo_o_null"
        },
        "processing_notes": "descripcion_detallada_del_estado",
        "next_action_required": "accion_que_debe_tomar_el_usuario_o_sistema"
    }
    """,
    description="Procesa pagos de gastos aprobados o gestiona estados pendientes",
    output_key="payment_result"
)

# --- 2. Create the SequentialAgent ---
expense_processing_pipeline = SequentialAgent(
    name="ExpenseProcessingPipeline",
    sub_agents=[
        receipt_digitizer_agent,
        expense_categorizer_agent, 
        policy_validator_agent,
        approval_email_sender_agent,
        approval_router_agent,
        payment_processor_agent
    ],
    description="Pipeline completo para procesamiento de gastos con aprobación por email",
)

# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = expense_processing_pipeline

# --- Funciones adicionales para integración con webhook ---

def handle_webhook_approval(transaction_id: str, decision: str, comments: str = "") -> Dict[str, Any]:
    """
    Maneja las respuestas de aprobación que vienen del webhook.
    Esta función se puede llamar cuando el webhook recibe una respuesta.
    
    Args:
        transaction_id: ID de la transacción
        decision: "approved" o "rejected"
        comments: Comentarios opcionales del aprobador
        
    Returns:
        Dict con el resultado del procesamiento
    """
    try:
        print(f"🔄 Procesando respuesta de webhook: {decision} para {transaction_id[:8]}")
        
        if decision == "approved":
            # Aquí podrías continuar el pipeline desde el punto de pago
            # O actualizar una base de datos, etc.
            result = {
                "status": "approved",
                "transaction_id": transaction_id,
                "decision": decision,
                "comments": comments,
                "next_action": "process_payment",
                "message": "Gasto aprobado, procediendo al pago"
            }
        elif decision == "rejected":
            result = {
                "status": "rejected", 
                "transaction_id": transaction_id,
                "decision": decision,
                "comments": comments,
                "next_action": "notify_employee",
                "message": "Gasto rechazado, notificando al empleado"
            }
        else:
            result = {
                "status": "error",
                "message": f"Decisión inválida: {decision}"
            }
            
        # Enviar email de confirmación
        send_confirmation_email(result)
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error procesando respuesta de webhook: {str(e)}"
        }

def get_expense_status(transaction_id: str) -> Dict[str, Any]:
    """
    Consulta el estado de un gasto por su transaction_id.
    Útil para integrar con sistemas externos.
    """
    # En una implementación real, consultarías una base de datos
    # Por ahora, devolvemos un placeholder
    return {
        "transaction_id": transaction_id,
        "status": "pending_approval",
        "message": "Esta función requiere integración con base de datos"
    }