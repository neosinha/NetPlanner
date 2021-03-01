
var serverLocation = location.host; 
var server = "http://" + serverLocation ;
console.log("Location: "+ server); 



var view = new UIViews();
var websx = new WebServices();

function appInit() {
	getSystemInfo();
}

function drawView() {
	appNavBar();
	view.loadLandingView();
	updatePerSecond();
	updatePer10Second();
}

var serialnum = null; 
var clock;


function updateClock() {
	var dt = new Date();
	$('#clock').html( dt.toLocaleString()); 
}

function updatePerSecond() {
	updateClock();
	setTimeout(updatePerSecond, 1000);
}


function updatePer10Second() {
    websx.getstats();
	setTimeout(updatePer10Second, 10000);
}




function getSystemInfo() {
	var urlx = 'http://' + server + '/getsysteminfo'; 
	console.log('Sys: '+ urlx);
	ajaxLoad(getsystem_callback, urlx); 
}


var systemModel = null; 
var networkObj = null; 

function getsystem_callback(respx) {
	console.log(respx);
	systemModel = JSON.parse(respx); 
	networkObj = systemModel['network'];
	
	drawView();
	
}
