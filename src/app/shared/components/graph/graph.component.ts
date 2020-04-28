import { Component, OnInit } from '@angular/core';
import ReconnectingWebSocket from 'reconnecting-websocket';

import * as _ from 'lodash';
import * as Highcharts from 'highcharts/highstock';
import HighchartsMore from 'highcharts/highcharts-more';
HighchartsMore(Highcharts);


@Component({
  selector: 'app-graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.scss']
})


export class GraphComponent implements OnInit {

  constructor() { }

  public chartOptions: Highcharts.Options = {
    series: [{
      data: [],
      type: 'candlestick'
    }],
    title:{
      text:"BTC Day"
    }
  };

  public Highcharts: typeof Highcharts = Highcharts;
  public socket;
  public candles: any;
  public updateFlag: boolean = false;



  ngOnInit() { this.setupWebSocket() }

  setupWebSocket() {
    
    this.socket = new ReconnectingWebSocket("wss://rix9fti73l.execute-api.us-east-1.amazonaws.com/prod");

    this.socket.onopen = (event) => {
      let data = {"action": "getWebsocketPrices"};
      this.socket.send(JSON.stringify(data));
    };

    this.socket.onmessage = (message) => {
      this.updateFlag = false;
      let test = JSON.parse(message.data)
      this.candles = test.prices;
      let newData = [];
      _.forEach(this.candles, (item) => {
        console.log(item.t)
        let mean = ((item.l + item.o + item.o + item.h) / 4);
        newData.push([item.o, item.h, item.l, item.c]);
        this.chartOptions.series[0]['data'] = newData;
      });
      this.updateFlag = true;
    };
  }

}
