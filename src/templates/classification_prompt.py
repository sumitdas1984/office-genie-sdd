from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent
CATEGORIES = [
    {"name": "IT", "description": "Hardware, software, access/permissions, network, security issues", "subcategories": ["Hardware", "Software", "Access/Permissions", "Network", "Security"]},
    {"name": "HR", "description": "Leave, benefits, policies, employee records", "subcategories": ["Leave", "Benefits", "Policies", "Employee Records"]},
    {"name": "Payroll", "description": "Payslip, deductions, reimbursements, tax", "subcategories": ["Payslip", "Deductions", "Reimbursements", "Tax"]},
    {"name": "Admin", "description": "Facilities, travel, supplies, miscellaneous", "subcategories": ["Facilities", "Travel", "Supplies", "Miscellaneous"]},
]
EXAMPLES = [
    {"message": "My password expired and I can't login to my laptop", "category": "IT", "subcategory": "Access/Permissions"},
    {"message": "I want to apply for 5 days of annual leave", "category": "HR", "subcategory": "Leave"},
    {"message": "My payslip shows wrong deductions this month", "category": "Payroll", "subcategory": "Deductions"},
    {"message": "The conference room projector is not working", "category": "Admin", "subcategory": "Facilities"},
    {"message": "I need to reorder printer paper for my floor", "category": "Admin", "subcategory": "Supplies"},
    {"message": "My screen flickers when I plug in the charger", "category": "IT", "subcategory": "Hardware"},
]


def render_prompt(message: str, employee_id: str, department: str) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("classification_prompt.j2")
    return template.render(
        categories=CATEGORIES,
        examples=EXAMPLES,
        message=message,
        employee_id=employee_id,
        department=department,
    )