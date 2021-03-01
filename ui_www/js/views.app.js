// file holds the code which designs the UI views
// or bigger/composite UI view elements
ui = new Bootstrap();


var pktMetrics = null;

var UIViews = function() {

    this.statsViewInit = function() {
        var v = ui.createElement('div', 'statsview');
        //<canvas id="myChart" width="400" height="400"></canvas>
        var can = ui.createElement('canvas', 'statschart');
        can.setAttribute('width', '480');
        can.setAttribute('height', '480');

        v.appendChild(can);

        return v;
    }


    this.updatepktstats = function(msg) {
        console.log('Stats: '+ msg);
        var pktstats = JSON.parse(msg);
        var divx = document.getElementById('statsview');
        divx.innerHTML = '';

        for (i=0; i < pktstats.length; i++) {
            var pktst = pktstats[i];
            var p = ui.createElement('p', 'intf'+i);
            var intfname = pktst['intf'];

            if (!pktMetrics.hasOwnProperty(intfname)) {
                pktMetrics[intfname] = new Array();
            }

            var datex = new Date(pktst['epoch']);
            p.innerHTML = '<em>'+pktst['intf']+'</em>' + ' '+ datex.toString()  + ' '+ pktst['stats'][0];
            divx.appendChild(p);

            pktMetrics.push({'label' : datex.toString(), 'data' : pktst['stats'][0];})
            if (pktMetrics.length > 5) {
                pktMetrics.pop();
            }

        }
    }




   this.loadLandingView = function() {

		var h1x = ui.h3(null, '', [{'name' : 'class', 'value' : 'mainlogo text-center' }]);
		var jum = ui.jumbotron('view1', h1x,' bg-basic');


		//create tab area
		var tabs = new Array();


		tabs.push({'name' : "<span class='maintab'>System</span>" ,
			'content' : systemView() });

		tabs.push({'name' : "<span class='maintab'>Interfaces</span>" ,
					'content' : networkInfo() });

		tabs.push({'name' : "<span class='maintab'>Stats</span>" ,
					'content' : view.statsViewInit() });


		tabs.push({'name' : "<span class='maintab'>Firewall</span>" ,
					'content' : firewallView() });

		navtabs= ui.navtabs('tabbed', 'justified bg-basic text-warning', tabs );


		//var inpbar = jum.appendChild(inpx2);
		/*var clockdiv = ui.createElement('div', 'clock');
		clockdiv.setAttribute('class', 'clock');
		jum.appendChild(clockdiv);
		*/

		//jum.appendChild(ui.hr() );
		//var guagearea = ui.createElement('div', 'guagearea');
		//guagearea.appendChild(productionView1());

		//jum.appendChild(packetLayout());
		var resultarea = ui.createElement('div', 'results');

		var notifyarea = ui.createElement('div', 'notify');

		//jum.appendChild(farStatusForm());
		jum.appendChild(navtabs);
//		/jum.appendChild(guagearea);
		jum.appendChild(resultarea);

		//jum.appendChild(xmlarea);
		jum.appendChild(notifyarea);



		ui.addSubViewToMain([jum]);

		$('#modalheader').html('');
		$('#modalbody').html('uuuu');
		$('#modalfooter').html('');

		$('#serialnumber').val('1917Q-20112');
		$('#partnum').val('800939-00-04');
    }


};


function appNavBar() {
	//navbar = ui.navbar("navarea", '<img align="middle" class="logo-img" src="img/logo-header-psi.png"></img>');
	navbar = ui.navbar("navarea", '<span class="brand">'+
								   '<img class="logo-img img-rounded pull-left" src="img/big-datax64.png"></img>'+
								   '<span class="brandtext">NetPlanner</span>'+
								   '</span>' + 
								   '<span class="clock" id="clock">Clock</span>'
								   );
	ui.addSubViewToMain([navbar]);
}


function loadPanels() {
	
}

function clicker() {
	alert('Clicked..');
}

function systemView() {
	var divx = ui.createElement('div', 'systemview');
	var hr = ui.hr();
	hr.setAttribute('class', 'top');
	divx.appendChild(hr);
	return divx; 
}

function networkInfo() {
	var divx = ui.createElement('div', 'networkview');
	var interfaces = []; 
	for(var k in networkObj) interfaces.push(k);
	var header = ['Interface', 'MAC', 'IPv4' , 'Active'];
	var tbldata = new Array();
	for (i=0; i < interfaces.length; i++) {
	    var active = false;

		var intf = interfaces[i];
		var netport = networkObj[intf];
		console.log('==' + interfaces[i]);
		console.log(intf + ':' + JSON.stringify(netport) );
		var mac = ''; 
		var ipv4 = '';
		var ipv6 = '';

		if ('mac' in netport) {
			mac = netport['mac']['addr'];
			mac = mac.toUpperCase();
		}
		
		if ('ipv4' in netport) {
			ipv4 = netport['ipv4']['addr'] + '<BR>' + netport['ipv4']['netmask'] + '<BR>' + netport['ipv4']['broadcast'];
			if (netport['ipv4'] === "")  {
			    active = false;
			} else {
			    active = true;
			}
		}


		if ('ipv6' in netport) {
			ipv6 = netport['ipv6']['addr'] + '<BR>' + netport['ipv6']['netmask']; 
		}
		
		
		if (intf.startsWith('e')) {
		    intf = '<img class="neticon" src="img/eth0-32x32.png">' + '<BR>'+intf + '</img>';
		}
		
		//tbldata.push( [intf, mac.toUpperCase(), ipv4.toUpperCase(), ipv6.toUpperCase(), 'Active'] );
		if (active) {
		    tbldata.push( [intf, mac.toUpperCase(), ipv4.toUpperCase(),  'Active'] );
		}
	}
	
	var tbl = ui.table('networktable', 'striped', header, tbldata );
	
	divx.appendChild(tbl);
	 
	var hr = ui.hr();

	hr.setAttribute('class', 'top');
	divx.appendChild(hr);
	return divx; 
}

function firewallView() {
	var divx = ui.createElement('div', 'networkview');
	var hr = ui.hr();
	hr.setAttribute('class', 'top');
	divx.appendChild(hr);
	return divx; 
}

