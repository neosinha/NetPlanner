# CherryPy + Bootstrap + MermaidJS Netplan Visualizer
# Folder structure:
# - app.py (this file)
# - static/
#   - mermaid.min.js
#   - bootstrap.min.css
# - templates/
#   - index.html

import cherrypy
import os
import yaml

class NetplanVisualizer:
    @cherrypy.expose
    def index(self):
        with open("./ui_www/index.html") as f:
            return f.read()

    @cherrypy.expose
    def generate(self, yaml_input=None):
        try:
            data = yaml.safe_load(yaml_input)
            interfaces = data.get("network", {}).get("ethernets", {})
            diagram = "graph TD\n  Netplan[Netplan Config]\n"
            for iface, settings in interfaces.items():
                label = "DHCP" if settings.get("dhcp4") else \
                    "<br>".join(settings.get("addresses", ["Static"]))
                diagram += f"  Netplan --> {iface}[{iface}<br>{label}]\n"
            return diagram
        except Exception as e:
            return f"graph TD\n  Error[Error parsing YAML: {str(e)}]"

    @cherrypy.expose
    def save(self, yaml_input=None, mermaid_output=None):
        with open("saved_netplan.yaml", "w") as f:
            f.write(yaml_input)
        with open("saved_diagram.mmd", "w") as f:
            f.write(mermaid_output)
        return "Saved!"

if __name__ == '__main__':
    cherrypy.quickstart(NetplanVisualizer(), '/', {
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath('./ui_www')
        }
    })
