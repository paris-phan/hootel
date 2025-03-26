import os
import re
import glob

def update_template(file_path):
    """
    Update a Django template file to use the dynamic base template from context processor.
    """
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Only process files that extend from base.html
    if "{% extends 'base/base.html' %}" in content or '{% extends "base/base.html" %}' in content:
        # Replace extends statement with dynamic template
        content = re.sub(
            r'{% extends [\'"]base/base.html[\'"] %}',
            '{% extends base_template %}',
            content
        )
        
        # Write updated content back to file
        with open(file_path, 'w') as file:
            file.write(content)
        return True
    return False

def main():
    """
    Update all Django templates to use the dynamic base template.
    """
    # Define the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, 'templates')
    
    # Find all HTML templates, excluding the base templates
    templates = []
    for pattern in ['**/*.html', '*.html']:
        templates.extend(glob.glob(os.path.join(templates_dir, pattern), recursive=True))
    
    # Filter out base templates
    base_templates = [
        os.path.join(templates_dir, 'base/base.html'),
        os.path.join(templates_dir, 'base/patron_base.html'),
        os.path.join(templates_dir, 'base/librarian_base.html')
    ]
    templates = [t for t in templates if t not in base_templates]
    
    # Update each template
    updated = 0
    for template in templates:
        if update_template(template):
            print(f"Updated: {os.path.relpath(template, base_dir)}")
            updated += 1
    
    print(f"\nTotal templates updated: {updated}")

if __name__ == "__main__":
    main() 