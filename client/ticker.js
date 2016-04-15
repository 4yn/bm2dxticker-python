jQuery(function($){

	var WebSocket = window.WebSocket || null;
	var Deferred = $.Deferred.bind($);

	if(!WebSocket){
		alert("No Websocket Support!");
		return;
	}

	var connector = new function Connector(){
		var _this = this; this.uri = ""; this.ws = null;
		this.connect = function Connector$connect(addr, port) {
			this.uri = "ws://"+addr+":"+port;
			return Deferred(function(defer){
				_this.ws = new WebSocket(_this.uri);
				_this.ws.onerror = function(e){
					_this.uri = "";
					_this.ws = null;
					defer.reject();
				};
				_this.ws.onopen = function(e){
					console.log("opened");
					setTimeout(_this.requestData,1000);
					defer.resolve();
				};
				_this.ws.onmessage = function(msg){
					$('#ticker').html(msg.data.split(' ').join("&nbsp;"));
				}
			});
		};
		this.send = function Connector$send(data){
			this.ws && this.ws.send(data);
		};
		this.requestData = function(){
			console.log("reqdata");
			if(_this.ws.readyState == 1){
				_this.send("1");
				setTimeout(_this.requestData,50);
			}
		}
	};

	$('#connect').click(function openConnection(){
		var remoteAddr = $('#ip-address').val();
		var remotePort = $('#port').val();
		$("#connect, #ip-address, #port").attr('disabled', true);

		connector.connect(remoteAddr, remotePort).done(function(){
			$('#setup').hide();
			$('#ticker,#ticker-ghost').show();
			connector.ws.onclose = function(){
				$('#setup').show();
				$('#ticker,#ticker-ghost').hide();
				$("#connect, #ip-address, #port").removeAttr('disabled');
			};
		}).fail(function(){
			$("#connect, #ip-address, #port").removeAttr('disabled');
		});
	});

});