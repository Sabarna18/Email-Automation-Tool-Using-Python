from jinja2 import FileSystemLoader , Environment , select_autoescape
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html" , "xml"]),
)

def render_template(template_name: str , context: dict ) -> str:
    
    tmpl = env.get_template(template_name)
    return tmpl.render(**context)