import { Component, OnInit, ApplicationRef } from '@angular/core';
import ReconnectingWebSocket from 'reconnecting-websocket';
import { btc_week } from '../../modules/btc_week';
import { btc_month } from '../../modules/btc_month';

import * as _ from 'lodash';
import * as Highcharts from 'highcharts';
import HighchartsMore from 'highcharts/highcharts-more';
HighchartsMore(Highcharts);


@Component({
  selector: 'app-graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.scss']
})


export class GraphComponent implements OnInit {

  constructor(private appRef: ApplicationRef) { }

  public Highcharts: typeof Highcharts = Highcharts;
  public socket;
  public candles: any;
  public updateFlag: boolean = false;

  public chartOptions: Highcharts.Options = {
    series: [{
      data: [],
      type: 'boxplot'
    }],
  };

  ngOnInit() { this.setupWebSocket() }

  async setupWebSocket() {
    
    this.socket = new ReconnectingWebSocket("wss://rix9fti73l.execute-api.us-east-1.amazonaws.com/prod");

    this.socket.onopen = (event) => {
      let data = {"action": "getPrices"};
      // this.socket.send(data);
      this.socket.send(JSON.stringify(data));
    };

    this.socket.onmessage = (message) => {
      this.candles = JSON.parse(message.data).prices;
      console.log(this.candles)
      // _.forEach(this.candles, (item) => {
      //   this.chartOptions.series[0]['data'].push([item.h, item.l, item.o, item.c])
      // });
      this.chartOptions.series[0]['data'].push(10, 1, 4, 5)
      this.updateFlag = true;
      this.appRef.tick();
    };
  }

}
