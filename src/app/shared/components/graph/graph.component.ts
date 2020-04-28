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

  public Highcharts: typeof Highcharts = Highcharts;

  public socket;
  public symbol = 'BTC';
  public timeframe = 'Minute';

  public chartOptions: Highcharts.Options = {
    series: [{
      data: [],
      type: 'candlestick'
    }],
    title:{
      text:`BTC ${this.timeframe}`
    }
  };


  public timeframes = [
    {
      'timeframe': 'Month',
      'table': 'BTC_month',
      'ttl': 0,
      'gap': 2628000,
      'datapoints': 0
    },
    {
      'timeframe': 'Week',
      'table': 'BTC_week',
      'ttl': 0,
      'gap': 604800,
      'datapoints': 0
    },
    {
      'timeframe': 'Day',
      'table': 'BTC_day',
      'ttl': 157680000,
      'gap': 86400,
      'datapoints': 1825
    },
    {
      'timeframe': '4 Hour',
      'table': 'BTC_four_hour',
      'ttl': 15768000,
      'gap': 14400,
      'datapoints': 1095
    },
    {
      'timeframe': 'Hour',
      'table': 'BTC_hour',
      'ttl': 2628000,
      'gap': 3600,
      'datapoints': 730
    },
    {
      'timeframe': '15 Minute',
      'table': 'BTC_fifteen_minute',
      'ttl': 604800,
      'gap': 900,
      'datapoints': 672
    },
    {
      'timeframe': 'Minute',
      'table': 'BTC_minute',
      'ttl': 86400,
      'gap': 60,
      'datapoints': 1440
    },
  ]

  public candles: any;
  public updateFlag: boolean = false;
  public newWebsocket: boolean = true;
  public websocketLastTimestamp = 0;


  ngOnInit() {
    this.socket = new ReconnectingWebSocket("wss://rix9fti73l.execute-api.us-east-1.amazonaws.com/prod");
    this.setupWebSocket();
  }

  newWebSocket(timeframe) {
    console.log(`triggered ${timeframe}`)
    if (timeframe !== this.timeframe) {
      console.log('different!')
      this.timeframe = timeframe;
      this.newWebsocket = true;
      this.updateFlag = false;
      this.chartOptions.series[0]['data'] = [];
      this.updateFlag = true;
      _.forEach(this.timeframes, (item) => {
        if (item.timeframe === timeframe) {
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
      this.setupWebSocket();
    }
  }

  setupWebSocket() {
    console.log('triggere')
    this.socket.onopen = (event) => {
      console.log('opened')
      _.forEach(this.timeframes, (item) => {
        if (item.timeframe === this.timeframe) {
          console.log(`item: ${item}`)
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
      console.log('message!')
      this.updateFlag = false;
      let candles = JSON.parse(message.data).prices;
      if (this.newWebsocket) {
        console.log('new websocket')
        let newData = [];
        _.forEach(candles, (item) => {
          newData.push([item.t, item.o, item.h, item.l, item.c]);
        });
        this.websocketLastTimestamp = candles[candles.length - 1]['t'];
        this.chartOptions.title.text = `BTC ${this.timeframe}`
        this.chartOptions.series[0]['data'] = newData;
        this.newWebsocket = false;
      }
      else {
        let latestCandle = candles[candles.length - 1];
        if (latestCandle['t'] > this.websocketLastTimestamp) {
          console.log('putting new candle in')
          this.chartOptions.series[0]['data'].shift();
          this.chartOptions.series[0]['data'].push([latestCandle['o'], latestCandle['h'], latestCandle['l'], latestCandle['c']]);
          this.websocketLastTimestamp = latestCandle['t']
        }
        else {
          console.log('updating candle')
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
