## ejecutar webhook_server.py
source venv/bin/activate

uvicorn webhook_server:app --reload --host 0.0.0.0 --port 8001

## ejecturar el agente webhook_procesamiento_gastos
(.venv) ➜  Sequential_agent git:(main)  adk web

## ejemplos para el agente y enviar correo:

Tengo un recibo de almuerzo de $45 en McDonald's del 2024-01-15" es para un reunión con el cliente

"Tengo un recibo de mouse ergonómico $508 en Falabella del 2025-04-13 por indicaciones médicas."
