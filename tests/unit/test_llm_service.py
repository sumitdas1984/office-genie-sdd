import pytest
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


class TestClassificationPromptTemplate:
    """Test Jinja2 classification prompt template rendering."""

    def test_template_renders_with_valid_prompt(self):
        """Template renders with message and contains category examples."""
        import os
        from src.services.llm_service import render_classification_prompt

        template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "src", "templates")
        rendered = render_classification_prompt(
            message="My printer is not working",
            employee_id="EMP-001",
            department="Engineering",
        )
        # Template should contain category examples
        assert "IT" in rendered
        assert "HR" in rendered
        assert "Payroll" in rendered
        assert "Admin" in rendered
        # Template should contain JSON output format hint
        assert "category" in rendered
        assert "subcategory" in rendered
        # Should include the actual message
        assert "My printer is not working" in rendered

    def test_template_contains_all_it_subcategories(self):
        """Template should include IT subcategories."""
        from src.services.llm_service import render_classification_prompt

        rendered = render_classification_prompt(
            message="Need access to SharePoint",
            employee_id="EMP-042",
            department="Marketing",
        )
        assert "Hardware" in rendered
        assert "Software" in rendered
        assert "Access/Permissions" in rendered

    def test_template_contains_all_hr_subcategories(self):
        """Template should include HR subcategories."""
        from src.services.llm_service import render_classification_prompt

        rendered = render_classification_prompt(
            message="I want to apply for leave",
            employee_id="EMP-042",
            department="Sales",
        )
        assert "Leave" in rendered
        assert "Benefits" in rendered
        assert "Policies" in rendered

    def test_template_contains_payroll_subcategories(self):
        """Template should include Payroll subcategories."""
        from src.services.llm_service import render_classification_prompt

        rendered = render_classification_prompt(
            message="My payslip is wrong",
            employee_id="EMP-042",
            department="Finance",
        )
        assert "Payslip" in rendered
        assert "Deductions" in rendered
        assert "Reimbursements" in rendered
        assert "Tax" in rendered

    def test_template_contains_admin_subcategories(self):
        """Template should include Admin subcategories."""
        from src.services.llm_service import render_classification_prompt

        rendered = render_classification_prompt(
            message="Need a new keyboard",
            employee_id="EMP-042",
            department="Operations",
        )
        assert "Facilities" in rendered
        assert "Travel" in rendered
        assert "Supplies" in rendered
        assert "Miscellaneous" in rendered