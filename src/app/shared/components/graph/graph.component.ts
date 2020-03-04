import { Component, OnInit } from '@angular/core';
import ReconnectingWebSocket from 'reconnecting-websocket';
import { btc_week } from '../../modules/btc_week';
import { btc_month } from '../../modules/btc_month';

@Component({
  selector: 'app-graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.scss']
})


export class GraphComponent implements OnInit {

  constructor(
  ) { }

  public socket;
  public candles: any;

  ngOnInit() { this.setupWebSocket() }

  setupWebSocket() {
    this.socket = new ReconnectingWebSocket("wss://rix9fti73l.execute-api.us-east-1.amazonaws.com/prod");
    console.log(this.socket)

    this.socket.onopen = (event) => {
      console.log(event)
      let data = {"action": "getPrices"};
      // this.socket.send(data);
      this.socket.send(JSON.stringify(data));
    };

    this.socket.onmessage = function(message) {
      console.log(message)
      this.candles = JSON.parse(message.data);
      console.log(this.candles)
    };
  }

}