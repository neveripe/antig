#!/usr/bin/env python3
"""
Build script for Energy Processor Web Application.
Bundles everything into a single self-contained HTML file that works with file:// protocol.

Usage:
    python build.py
"""

import sys
from pathlib import Path


def main():
    """Bundle the web application into a self-contained HTML file."""
    
    # Define paths
    web_dir = Path(__file__).parent
    project_root = web_dir.parent
    
    template_html = web_dir / "index.html"
    python_web_file = web_dir / "energy_processor_web.py"
    domain_models_file = project_root / "src" / "domain" / "models.py"
    
    dist_dir = web_dir / "dist"
    output_html = dist_dir / "index.html"
    
    # Validate inputs exist
    if not template_html.exists():
        print(f"[ERROR] Template not found: {template_html}")
        sys.exit(1)
    
    if not python_web_file.exists():
        print(f"[ERROR] Python web file not found: {python_web_file}")
        sys.exit(1)
        
    if not domain_models_file.exists():
        print(f"[ERROR] Domain models not found: {domain_models_file}")
        sys.exit(1)
    
    print("[BUILD] Building self-contained web application...")
    print(f"   Template: {template_html.name}")
    print(f"   Python: {python_web_file.name}")
    print(f"   Domain: {domain_models_file}")
    
    # Read template HTML
    html_content = template_html.read_text(encoding='utf-8')
    
    # Read Python files
    domain_models_code = domain_models_file.read_text(encoding='utf-8')
    web_processor_code = python_web_file.read_text(encoding='utf-8')
    
    # Remove the import statement from web processor (since we'll inline the models)
    web_processor_code = remove_domain_import(web_processor_code)
    
    # Combine Python code: domain models first, then web processor
    combined_python = f"""# ===== Domain Models (from src/domain/models.py) =====
{domain_models_code}

# ===== Web Processor (from energy_processor_web.py) =====
{web_processor_code}
"""
    
    # Create inline Python script tag
    inline_python_tag = f"""<script type="py" config='{{"packages": ["pandas", "matplotlib", "numpy"]}}'>
{combined_python}
    </script>"""
    
    # Find and replace the placeholder in HTML
    marker = "<!-- BUILD_INJECT_PYTHON_HERE -->"
    
    if marker in html_content:
        # Replace marker with inline Python
        html_content = html_content.replace(marker, inline_python_tag)
    else:
        # Fallback: replace the external script tag
        old_script = '<script type="py" config=\'{"packages": ["pandas", "matplotlib", "numpy"]}\' src="./energy_processor_web.py"></script>'
        
        if old_script in html_content:
            html_content = html_content.replace(old_script, inline_python_tag)
        else:
            print("[WARN] Warning: Could not find placeholder or script tag to replace")
            print("       Trying alternative approach...")
            # Try to find any PyScript tag with src
            import re
            pattern = r'<script type="py"[^>]*src="[^"]*"[^>]*></script>'
            match = re.search(pattern, html_content)
            if match:
                html_content = html_content.replace(match.group(0), inline_python_tag)
            else:
                print("[ERROR] Could not find PyScript tag to replace")
                sys.exit(1)
    
    # Create dist directory
    dist_dir.mkdir(exist_ok=True)
    
    # Write output
    output_html.write_text(html_content, encoding='utf-8')
    
    # Create .gitignore in dist/
    gitignore = dist_dir / ".gitignore"
    gitignore.write_text("# Generated files - do not commit\n*\n!.gitignore\n", encoding='utf-8')
    
    print("[SUCCESS] Build complete!")
    print(f"   Output: {output_html}")
    print(f"   Size: {output_html.stat().st_size:,} bytes")
    print(f"\n[INFO] Open {output_html} in your browser to use the app!")


def remove_domain_import(code: str) -> str:
    """Remove import statement for domain models since they'll be inlined."""
    lines = code.split('\n')
    filtered_lines = []
    
    for line in lines:
        # Skip the import line for domain models
        if 'from src.domain.models import' in line:
            # Replace with comment explaining what happened
            filtered_lines.append("# Domain models inlined by build script (was: from src.domain.models import ...)")
        else:
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)


if __name__ == "__main__":
    main()
