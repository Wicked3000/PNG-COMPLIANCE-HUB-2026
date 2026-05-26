import os

template_dir = r"d:\PNG COMPLIANCE HUB 2026\templates"

replacements = {
    "PNG Compliance Hub 2026": "{{ APP_NAME }} {{ TAX_YEAR }}",
    "2026 Tax Year": "{{ TAX_YEAR }} Tax Year",
    "IRC Tax Year 2026": "IRC Tax Year {{ TAX_YEAR }}",
    "IRC 2026": "IRC {{ TAX_YEAR }}",
    "2026 Resident SWT Brackets": "{{ TAX_YEAR }} Resident SWT Brackets",
    "2026 Resident Progressive Tax Brackets": "{{ TAX_YEAR }} Resident Progressive Tax Brackets",
    "2026 Resident Brackets": "{{ TAX_YEAR }} Resident Brackets",
    "2026 SBT Rate Bands": "{{ TAX_YEAR }} SBT Rate Bands",
    "2026 SBT Annual Declaration": "{{ TAX_YEAR }} SBT Annual Declaration",
    "2026 Financial Year": "{{ TAX_YEAR }} Financial Year",
    "File 2026 Declaration": "File {{ TAX_YEAR }} Declaration",
    "Submit 2026 SBT Declaration": "Submit {{ TAX_YEAR }} SBT Declaration",
    "SBT Status 2026": "SBT Status {{ TAX_YEAR }}",
    "SBT Status - 2026": "SBT Status - {{ TAX_YEAR }}",
    "2026 IRC Filing Calendar": "{{ TAX_YEAR }} IRC Filing Calendar",
    "for the 2026 Tax Year": "for the {{ TAX_YEAR }} Tax Year",
    "G-FORM 2026": "G-FORM {{ TAX_YEAR }}",
}

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    # Handle PDF standalone templates separately since they don't have context processors
    # But actually, they DO get rendered via render_to_string which includes context processors if RequestContext is used.
    # Wait, in reports/views.py, _generate_pdf_response uses render_to_string. Wait, does it pass request?
    # `render_to_string(template_name, context)` without `request` does NOT run context processors!
    # So PDF templates won't have {{ APP_NAME }} or {{ TAX_YEAR }}.
    # We should use `{% now "Y" %}` or explicitly pass `tax_year` to the context in `reports/views.py`.
    
    is_pdf = "pdf" in filepath.replace('\\', '/')
    for old, new in replacements.items():
        if is_pdf:
            # For PDFs, we'll replace with template tags that don't need context processor, or pass it manually.
            # Actually, `tax_year` is not passed to GST Return PDF. We can use `{% now "Y" %}` for "2026"
            content = content.replace(old, old.replace("2026", '{% now "Y" %}'))
        else:
            content = content.replace(old, new)

    if original != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filepath}")

for root, _, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            update_file(os.path.join(root, file))

print("Done updating templates.")
