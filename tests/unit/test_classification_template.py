def test_template_renders_without_error():
    from src.templates.classification_prompt import render_prompt
    result = render_prompt(
        message="My laptop is broken",
        employee_id="EMP-001",
        department="Engineering"
    )
    assert isinstance(result, str)
    assert len(result) > 100

def test_template_includes_category_definitions():
    from src.templates.classification_prompt import render_prompt
    result = render_prompt("test", "EMP-001", "Engineering")
    assert "IT" in result
    assert "HR" in result
    assert "Payroll" in result
    assert "Admin" in result

def test_template_includes_examples():
    from src.templates.classification_prompt import render_prompt
    result = render_prompt("test", "EMP-001", "Engineering")
    assert "Password Reset" in result or "printer" in result.lower()