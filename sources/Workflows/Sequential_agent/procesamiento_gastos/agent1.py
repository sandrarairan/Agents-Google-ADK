# Part of agent.py --> Follow https://google.github.io/adk-docs/get-started/quickstart/ to learn the setup
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools import google_search
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
GEMINI_MODEL = "gemini-2.0-flash"

# --- 1. Define Sub-Agents for Each Pipeline Stage ---

# Receipt Digitizer Agent
# Extracts and digitizes information from receipt images or documents
receipt_digitizer_agent = LlmAgent(
    name="ReceiptDigitizerAgent",
    model=GEMINI_MODEL,
    tools=[google_search],
    instruction="""You are a Receipt Digitization Expert.
Your task is to extract structured information from receipt data provided by the user.

Extract the following information:
- Date of purchase (format: YYYY-MM-DD)
- Vendor/Merchant name
- Total amount (numeric value)
- Currency
- Items purchased (if detailed)
- Tax amount (if available)
- Payment method (if mentioned)

If the user provides an image description or receipt text, parse it carefully.
If information is missing or unclear, mark it as "NOT_FOUND".

Output the extracted information in this JSON format:
```json
{
    "date": "YYYY-MM-DD",
    "vendor": "Merchant Name",
    "total_amount": 0.00,
    "currency": "USD",
    "items": ["item1", "item2"],
    "tax_amount": 0.00,
    "payment_method": "Credit Card"
}
```

Output *only* the JSON structure, no additional text.
""",
    description="Extracts structured data from receipts and invoices.",
    output_key="digitized_receipt"
)

# Expense Categorizer Agent
# Categorizes expenses based on company policies and merchant information
expense_categorizer_agent = LlmAgent(
    name="ExpenseCategorizerAgent",
    model=GEMINI_MODEL,
    tools=[google_search],
    instruction="""You are an Expense Categorization Expert.
Your task is to categorize expenses based on the digitized receipt information.

**Receipt Information:**
```json
{digitized_receipt}
```

**Available Categories:**
- MEALS_ENTERTAINMENT: Restaurant meals, client entertainment
- TRANSPORTATION: Flights, hotels, car rental, taxi, gas
- OFFICE_SUPPLIES: Stationery, equipment, software
- MARKETING: Advertising, promotional materials, events
- PROFESSIONAL_SERVICES: Legal, consulting, accounting
- UTILITIES: Phone, internet, electricity (if applicable)
- TRAINING: Courses, certifications, books
- MISCELLANEOUS: Other business expenses

**Categorization Rules:**
1. Analyze vendor name and items to determine appropriate category
2. Use Google search if needed to identify unfamiliar vendors
3. If uncertain, default to MISCELLANEOUS
4. Consider common business expense patterns

Output in this JSON format:
```json
{
    "category": "CATEGORY_NAME",
    "subcategory": "specific subcategory if applicable",
    "confidence_score": 0.95,
    "reasoning": "Brief explanation of categorization"
}
```

Output *only* the JSON structure, no additional text.
""",
    description="Categorizes expenses based on vendor and items.",
    output_key="expense_category"
)

# Policy Validator Agent
# Validates expenses against company policies and spending limits
policy_validator_agent = LlmAgent(
    name="PolicyValidatorAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Company Policy Validation Expert.
Your task is to validate expenses against company policies.

**Receipt Information:**
```json
{digitized_receipt}
```

**Category Information:**
```json
{expense_category}
```

**Company Policy Rules:**
1. MEALS_ENTERTAINMENT: Max $75 per person per meal, receipts required >$25
2. TRANSPORTATION: Pre-approval required for flights >$500
3. OFFICE_SUPPLIES: Max $200 per purchase without approval
4. MARKETING: Pre-approval required for campaigns >$1000
5. PROFESSIONAL_SERVICES: Must have contract/PO number
6. TRAINING: Pre-approval required, max $2000 per year per employee
7. General: All expenses must be business-related and reasonable

**Validation Checks:**
- Amount limits for category
- Required approvals
- Receipt requirements
- Business purpose validation
- Date validity (not future dated, within policy timeframe)

Output in this JSON format:
```json
{
    "is_valid": true,
    "violations": [],
    "warnings": ["warning if any"],
    "required_approvals": ["manager", "finance"],
    "additional_documentation_needed": ["contract", "business_purpose"],
    "validation_notes": "Summary of validation results"
}
```

Output *only* the JSON structure, no additional text.
""",
    description="Validates expenses against company policies.",
    output_key="policy_validation"
)

# Approval Router Agent
# Routes expenses to appropriate approvers based on amount and category
approval_router_agent = LlmAgent(
    name="ApprovalRouterAgent",
    model=GEMINI_MODEL,
    instruction="""You are an Approval Routing Expert.
Your task is to determine the appropriate approval workflow for expenses.

**Receipt Information:**
```json
{digitized_receipt}
```

**Category Information:**
```json
{expense_category}
```

**Policy Validation:**
```json
{policy_validation}
```

**Approval Routing Rules:**
1. Auto-approved: <$50, policy compliant, standard categories
2. Manager approval: $50-$500, policy compliant
3. Finance approval: >$500, or policy violations
4. Executive approval: >$2000, or high-risk categories
5. Rejection: Major policy violations, fraudulent expenses

**Routing Logic:**
- Consider amount, category, policy compliance
- Route to lowest appropriate level
- Escalate if violations detected
- Provide clear reasoning for routing decision

Output in this JSON format:
```json
{
    "approval_level": "AUTO_APPROVED|MANAGER|FINANCE|EXECUTIVE|REJECTED",
    "approver_email": "approver@company.com",
    "priority": "LOW|MEDIUM|HIGH",
    "estimated_approval_time": "2 hours",
    "routing_reason": "Explanation of routing decision",
    "next_steps": ["action1", "action2"]
}
```

Output *only* the JSON structure, no additional text.
""",
    description="Routes expenses to appropriate approvers.",
    output_key="approval_routing"
)

# Payment Processor Agent
# Processes approved expenses for payment
payment_processor_agent = LlmAgent(
    name="PaymentProcessorAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Payment Processing Expert.
Your task is to prepare approved expenses for payment processing.

**Receipt Information:**
```json
{digitized_receipt}
```

**Approval Routing:**
```json
{approval_routing}
```

**Processing Logic:**
1. Only process if approval_level is not "REJECTED"
2. Generate payment instructions based on expense details
3. Calculate reimbursement amount (if employee expense)
4. Determine payment method and timeline
5. Create payment tracking information

**Payment Methods:**
- Direct deposit (employees)
- Check (vendors)
- Wire transfer (large amounts)
- Corporate card payment (direct vendor payments)

Output in this JSON format:
```json
{
    "payment_status": "READY_FOR_PAYMENT|PENDING_APPROVAL|REJECTED",
    "payment_method": "DIRECT_DEPOSIT|CHECK|WIRE|CORPORATE_CARD",
    "payment_amount": 0.00,
    "payment_timeline": "2-3 business days",
    "tracking_number": "TRK-20240101-001",
    "accounting_codes": {
        "expense_account": "6100",
        "cost_center": "CC001",
        "project_code": "PRJ001"
    },
    "payment_instructions": "Detailed payment processing instructions"
}
```

Output *only* the JSON structure, no additional text.
""",
    description="Processes approved expenses for payment.",
    output_key="payment_processing"
)

# --- 2. Create the SequentialAgent ---
# This agent orchestrates the expense processing pipeline
expense_pipeline_agent = SequentialAgent(
    name="ExpenseProcessingPipeline",
    sub_agents=[
        receipt_digitizer_agent,
        expense_categorizer_agent,
        policy_validator_agent,
        approval_router_agent,
        payment_processor_agent
    ],
    description="Executes a complete expense processing workflow from receipt to payment.",
    # The agents will run in order: Digitizer -> Categorizer -> Validator -> Router -> Processor
)

# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = expense_pipeline_agent