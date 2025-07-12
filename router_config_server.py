
import cherrypy
import zipfile
import io

class ConfigServer(object):
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def generate_config(self):
        data = cherrypy.request.json
        interfaces = data.get("interfaces", [])
        
        if len(interfaces) < 4:
            cherrypy.response.status = 400
            return "Not enough interfaces"

        wan = interfaces[0]
        lan1 = interfaces[1]
        lan2 = interfaces[2]
        lan3 = interfaces[3]

        netplan = f"""network:
  version: 2
  renderer: networkd
  ethernets:
    {wan}:
      dhcp4: true
    {lan1}:
      dhcp4: no
      addresses: [172.16.100.1/24]
    {lan2}:
      dhcp4: no
      addresses: [172.16.200.1/24]
    {lan3}:
      dhcp4: no
      addresses: [172.16.300.1/24]
"""

        dnsmasq = """
dhcp-range=10.10.10.10,10.10.10.100,255.255.255.0,24h
dhcp-range=10.10.20.10,10.10.20.100,255.255.255.0,24h
dhcp-range=10.10.30.10,10.10.30.100,255.255.255.0,24h
log-queries
"""

        firewall = f"""#!/bin/bash
iptables -F
iptables -P FORWARD DROP
iptables -A FORWARD -i {wan} -o {lan1} -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i {lan1} -o {wan} -j ACCEPT
"""

        vxlan_service = f"""[Unit]
Description=VXLAN overlay network setup
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/setup-vxlan.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
"""

        install_sh = f"""#!/bin/bash
sudo cp netplan.yaml /etc/netplan/01-vxlan.yaml
sudo cp dnsmasq.conf /etc/dnsmasq.conf
sudo cp firewall.sh /usr/local/sbin/firewall.sh
sudo cp vxlan-setup.service /etc/systemd/system/vxlan-setup.service
sudo chmod +x /usr/local/sbin/firewall.sh
sudo systemctl daemon-reload
sudo systemctl enable vxlan-setup
sudo systemctl enable dnsmasq
sudo systemctl start vxlan-setup
sudo systemctl restart dnsmasq
"""

        memzip = io.BytesIO()
        with zipfile.ZipFile(memzip, "w") as z:
            z.writestr("netplan.yaml", netplan)
            z.writestr("dnsmasq.conf", dnsmasq)
            z.writestr("firewall.sh", firewall)
            z.writestr("vxlan-setup.service", vxlan_service)
            z.writestr("install.sh", install_sh)
        cherrypy.response.headers['Content-Type'] = 'application/zip'
        cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=router_config.zip'
        return memzip.getvalue()

if __name__ == "__main__":
    cherrypy.config.update({
        "server.socket_host": "0.0.0.0",
        "server.socket_port": 8080
    })
    cherrypy.quickstart(ConfigServer())
