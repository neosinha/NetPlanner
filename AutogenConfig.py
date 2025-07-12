import cherrypy
import yaml
from pathlib import Path

CONFIG_FILE = Path("config/network_config.yaml")
GENERATED_DIR = Path("generated")

class ConfigAPI(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return {"status": "CherryPy config generator API running"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def show(self):
        # show current YAML
        if CONFIG_FILE.exists():
            return yaml.safe_load(CONFIG_FILE.read_text())
        else:
            return {"error": "network_config.yaml not found"}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def update(self):
        # accept JSON payload and write back to YAML
        new_config = cherrypy.request.json
        with CONFIG_FILE.open("w") as f:
            yaml.safe_dump(new_config, f)
        return {"status": "updated"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def generate(self, which=None):
        config = yaml.safe_load(CONFIG_FILE.read_text())
        if which == "netplan":
            self.generate_netplan(config)
            return {"status": "netplan.yaml generated"}
        elif which == "dnsmasq":
            self.generate_dnsmasq(config)
            return {"status": "dnsmasq.conf generated"}
        elif which == "nftables":
            self.generate_nftables(config)
            return {"status": "nftables.conf generated"}
        else:
            return {"error": "missing or invalid 'which' parameter"}

    def generate_netplan(self, config):
        netplan = {
            "network": {
                "version": 2,
                "ethernets": {
                    config['interfaces']['wan']: {"dhcp4": True}
                },
                "vlans": {},
            }
        }
        for vlan in config['vlans']:
            netplan['vlans'][f"vlan{vlan['id']}"] = {
                "id": vlan['id'],
                "link": config['interfaces']['ap'],
                "addresses": [ vlan['subnet'].replace('0/24','1/24') ],
            }
        servers = config['servers']
        netplan['vlans'][f"vlan{servers['vlan']}"] = {
            "id": servers['vlan'],
            "link": config['interfaces']['servers'],
            "addresses": [ servers['subnet'].replace('0/24','1/24') ],
        }
        inspection = config['inspection']
        netplan['vlans'][f"vlan{inspection['vlan']}"] = {
            "id": inspection['vlan'],
            "link": config['interfaces']['inspection'],
            "addresses": [ inspection['static_ip'] ],
        }
        GENERATED_DIR.mkdir(exist_ok=True)
        (GENERATED_DIR / "netplan.yaml").write_text(yaml.dump(netplan, sort_keys=False))

    def generate_dnsmasq(self, config):
        lines = []
        for vlan in config['vlans']:
            lines.append(f"dhcp-range={vlan['subnet'].replace('0/24','1')},{vlan['dhcp_range']},12h")
        servers = config['servers']
        lines.append(f"dhcp-range={servers['subnet'].replace('0/24','1')},{servers['dhcp_range']},12h")
        GENERATED_DIR.mkdir(exist_ok=True)
        (GENERATED_DIR / "dnsmasq.conf").write_text("\n".join(lines))

    def generate_nftables(self, config):
        rules = []
        rules.append("table inet filter {")
        rules.append("  chain input {")
        rules.append("    type filter hook input priority 0;")
        rules.append("    policy drop;")
        rules.append("    iifname lo accept")
        rules.append("    ct state established,related accept")
        rules.append(f"    iifname {config['interfaces']['wan']} accept")

        # DHCP, DNS, ping
        for vlan in config['vlans']:
            rules.append(f"    iifname vlan{vlan['id']} udp dport 67 accept")
            rules.append(f"    iifname vlan{vlan['id']} udp dport 53 accept")
            rules.append(f"    iifname vlan{vlan['id']} icmp type echo-request accept")
            rules.append(f"    iifname vlan{vlan['id']} ip saddr != {vlan['subnet']} drop")
        servers = config['servers']
        rules.append(f"    iifname vlan{servers['vlan']} udp dport 67 accept")
        rules.append(f"    iifname vlan{servers['vlan']} udp dport 53 accept")
        rules.append(f"    iifname vlan{servers['vlan']} tcp dport 22 accept")
        rules.append(f"    iifname vlan{servers['vlan']} ip saddr != {servers['subnet']} drop")

        rules.append("    ip daddr 10.0.0.0/8 accept")

        rules.append("  }")

        rules.append("  chain forward {")
        rules.append("    type filter hook forward priority 0;")
        rules.append("    policy drop;")

        for vlan in config['vlans']:
            rules.append(f"    iifname vlan{vlan['id']} oifname {{")
            for vlan2 in config['vlans']:
                if vlan['id'] != vlan2['id']:
                    rules.append(f"      vlan{vlan2['id']}")
            rules.append("    } drop")

        for vlan in config['vlans']:
            rules.append(f"    iifname vlan{vlan['id']} oifname {config['interfaces']['wan']} accept")
        rules.append(f"    iifname vlan{servers['vlan']} oifname {config['interfaces']['wan']} accept")

        rules.append(f"    iifname vlan{config['inspection']['vlan']} drop")
        rules.append("  }")
        rules.append("}")
        GENERATED_DIR.mkdir(exist_ok=True)
        (GENERATED_DIR / "nftables.conf").write_text("\n".join(rules))

if __name__ == '__main__':
    cherrypy.quickstart(ConfigAPI(), '/', {
        '/': {
            'tools.sessions.on': False,
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        }
    })
