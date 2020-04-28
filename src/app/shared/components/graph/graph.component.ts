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
  public symbol = 'BTC';
  public timeframe = 'day';

  public timeframes = [
    {
      'timeframe': 'month',
      'table': 'BTC_month',
      'ttl': 0,
      'gap': 2628000,
      'datapoints': 0
    },
    {
      'timeframe': 'week',
      'table': 'BTC_week',
      'ttl': 0,
      'gap': 604800,
      'datapoints': 0
    },
    {
      'timeframe': 'day',
      'table': 'BTC_day',
      'ttl': 157680000,
      'gap': 86400,
      'datapoints': 1825
    },
    {
      'timeframe': 'four_hour',
      'table': 'BTC_four_hour',
      'ttl': 15768000,
      'gap': 14400,
      'datapoints': 1095
    },
    {
      'timeframe': 'hour',
      'table': 'BTC_hour',
      'ttl': 2628000,
      'gap': 3600,
      'datapoints': 730
    },
    {
      'timeframe': 'fifteen_minute',
      'table': 'BTC_fifteen_minute',
      'ttl': 604800,
      'gap': 900,
      'datapoints': 672
    },
    {
      'timeframe': 'minute',
      'table': 'BTC_minute',
      'ttl': 86400,
      'gap': 60,
      'datapoints': 1440
    },
  ]

  public candles: any;
  public updateFlag: boolean = false;
  public newWebsocket: boolean = false;
  public websocketLastTimestamp = 0;


  ngOnInit() { this.setupWebSocket() }

  setupWebSocket() {
    this.newWebsocket = true;

    this.socket = new ReconnectingWebSocket("wss://rix9fti73l.execute-api.us-east-1.amazonaws.com/prod");
    let test = 4
    this.socket.onopen = (event) => {
      _.forEach(this.timeframes, (item) => {
        if (item.timeframe === this.timeframe) {
          this.socket.send(JSON.stringify({
            'action': 'getWebsocketPrices',
            'symbol': this.symbol,
            'table': item.table,
            'ttl': item.ttl,
            'gap': item.gap,
            'datapoints': item.datapoints
          }));
        }
      });
    }

    this.socket.onmessage = (message) => {
      this.updateFlag = false;
      let candles = JSON.parse(message.data).prices;
      if (this.newWebsocket) {
        let newData = [];
        _.forEach(this.candles, (item) => {
          newData.push([item.o, item.h, item.l, item.c]);
        });
        this.websocketLastTimestamp = candles[-1]['t'];
        this.chartOptions.series[0]['data'] = newData;
        this.newWebsocket = false;
      }
      else {
        let latestCandle = candles[-1];
        if (latestCandle['t'] > this.websocketLastTimestamp) {
          this.chartOptions.series[0]['data'].shift();
          this.chartOptions.series[0]['data'].push([latestCandle['o'], latestCandle['h'], latestCandle['l'], latestCandle['c']]);
          this.websocketLastTimestamp = latestCandle['t']
        }
        else {
          this.chartOptions.series[0]['data'][-1]['o'] = latestCandle['o'];
          this.chartOptions.series[0]['data'][-1]['h'] = latestCandle['h'];
          this.chartOptions.series[0]['data'][-1]['l'] = latestCandle['l'];
          this.chartOptions.series[0]['data'][-1]['c'] = latestCandle['c'];
        }
      }
      this.updateFlag = true;
    };

  }


}
