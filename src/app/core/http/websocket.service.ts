import { Injectable } from '@angular/core';
import ReconnectingWebSocket from 'reconnecting-websocket';

@Injectable({
  providedIn: 'root'
})
export class WebsocketService {

  constructor() { }

  socket;
  public candles: any;

// Connect to the WebSocket and setup listeners
    setupWebSocket() {
        this.socket = new ReconnectingWebSocket("wss://rix9fti73l.execute-api.us-east-1.amazonaws.com/prod");

        this.socket.onopen = function(event) {
          let data = {"action": "getPrices"};
          this.socket.send(JSON.stringify(data));
      };

      this.socket.onmessage = function(message) {
        this.candles = JSON.parse(message.data);
        console.log(this.candles)
        // this.candles["messages"].forEach(function(message) {
        //     if ($("#message-container").children(0).attr("id") == "empty-message") {
        //         $("#message-container").empty();
        //     }
        //     if (message["username"] === username) {
        //         $("#message-container").append("<div class='message self-message'><b>(You)</b> " + message["content"]);
        //     } else {
        //         $("#message-container").append("<div class='message'><b>(" + message["username"] + ")</b> " + message["content"]);
        //     }
        //     $("#message-container").children().last()[0].scrollIntoView();
        // });
      };
    }
}
