from jinja2 import Environment, FileSystemLoader
import os

def render_xml_template(template_name, context, output_filename):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)
    rendered_content = template.render(context)

    os.makedirs('web', exist_ok=True)
    output_path = os.path.join('web', output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered_content)