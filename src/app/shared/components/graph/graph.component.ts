import { Component, OnInit } from '@angular/core';
import { HttpParams } from '@angular/common/http';
import ReconnectingWebSocket from 'reconnecting-websocket';

import { ApiService } from '../../../core/http/api.service';

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

  constructor(private apiService: ApiService) { }

  public Highcharts: typeof Highcharts = Highcharts;

  public socket;
  public symbol = 'BTC';
  public timeframe = 'Day';

  public chartOptions: Highcharts.Options = {
    chart: {
      zoomType: 'x'
    },
    title: {
        text: `Bitcoin / U.S. Dollar: Day Datapoints`
    },
    subtitle: {
        text: document.ontouchstart === undefined ?
            'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
    },
    xAxis: {
        type: 'datetime'
    },
    yAxis: {
        labels: {
            format: '${value}'
        },
        title: {
            text: 'Price (USD)'
        }
    },
    tooltip: {
      pointFormat: 'Price: ${point.y}<br>',
      shared: true
    },
    legend: {
        enabled: false
    },
    plotOptions: {
      area: {
        lineColor: '#00D080',
        fillOpacity: 0, 
        marker: {
            radius: 3
        },
        lineWidth: 3,
        states: {
            hover: {
                lineWidth: 2
            }
        },
        threshold: null
      }
    },
    annotations: [],
    series: [{
        type: 'area',
        data: [],
    }]
  };


  public timeframes = [
    {
      'timeframe': 'Minute',
      'buttonName': '1Min',
      'value': 'minute',
      'table': 'BTC_minute',
      'ttl': 86400,
      'gap': 60,
      'datapoints': 1440
    },
    {
      'timeframe': '15 Minute',
      'buttonName': '15Min',
      'value': 'fifteen_minute',
      'table': 'BTC_fifteen_minute',
      'ttl': 604800,
      'gap': 900,
      'datapoints': 672
    },
    {
      'timeframe': 'Hour',
      'buttonName': '1H',
      'value': 'hour',
      'table': 'BTC_hour',
      'ttl': 2628000,
      'gap': 3600,
      'datapoints': 730
    },
    {
      'timeframe': '4 Hour',
      'buttonName': '4H',
      'value': 'four_hour',
      'table': 'BTC_four_hour',
      'ttl': 15768000,
      'gap': 14400,
      'datapoints': 1095
    },
    {
      'timeframe': 'Day',
      'buttonName': '1D',
      'value': 'day',
      'table': 'BTC_day',
      'ttl': 157680000,
      'gap': 86400,
      'datapoints': 1825
    },
    {
      'timeframe': 'Week',
      'buttonName': '7D',
      'value': 'week',
      'table': 'BTC_week',
      'ttl': 0,
      'gap': 604800,
      'datapoints': 0
    },
    {
      'timeframe': 'Month',
      'buttonName': '1Mo',
      'value': 'month',
      'table': 'BTC_month',
      'ttl': 0,
      'gap': 2628000,
      'datapoints': 0
    },
  ]

  public candles: any;
  public updateFlag: boolean = false;
  public newWebsocket: boolean = true;
  public websocketLastTimestamp = 0;


  ngOnInit() {
    // this.socket = new ReconnectingWebSocket("wss://rix9fti73l.execute-api.us-east-1.amazonaws.com/prod");
    this.setGraph('day', 'Day');
  }

  setGraph(timeframe, displayName) {
    console.log(timeframe)
    let graph_params = new HttpParams().set('table', JSON.stringify([timeframe]));
    this.apiService.getSingleTable(graph_params).subscribe(data => {
      console.log(data)
      this.updateFlag = false;
      let newData = [];
      _.forEach(data[0]['tf_data'], (item) => {
        newData.push([item.t * 1000, item.c]);
      });
      this.chartOptions.series[0]['data'] = newData;
      this.chartOptions.title.text = `Bitcoin / U.S. Dollar: ${displayName} Datapoints`;
      this.updateFlag = true;
    });
  }

  // newWebSocket(timeframe) {
  //   console.log(`triggered ${timeframe}`)
  //   if (timeframe !== this.timeframe) {
  //     console.log('different!')
  //     this.timeframe = timeframe;
  //     this.newWebsocket = true;
  //     this.updateFlag = false;
  //     this.chartOptions.series[0]['data'] = [];
  //     this.updateFlag = true;
  //     _.forEach(this.timeframes, (item) => {
  //       if (item.timeframe === timeframe) {
  //         this.socket.send(JSON.stringify({
  //           'action': 'getWebsocketPrices',
  //           'symbol': this.symbol,
  //           'table': item.table,
  //           'ttl': item.ttl,
  //           'gap': item.gap,
  //           'datapoints': item.datapoints
  //         }));
  //       }
  //     });
  //     this.setupWebSocket();
  //   }
  // }

  // setupWebSocket() {
  //   this.socket.onopen = (event) => {
  //     console.log('opened')
  //     _.forEach(this.timeframes, (item) => {
  //       if (item.timeframe === this.timeframe) {
  //         console.log(`item: ${item}`)
  //         this.socket.send(JSON.stringify({
  //           'action': 'getWebsocketPrices',
  //           'symbol': this.symbol,
  //           'table': item.table,
  //           'ttl': item.ttl,
  //           'gap': item.gap,
  //           'datapoints': item.datapoints
  //         }));
  //       }
  //     });
  //   }

  //   this.socket.onmessage = (message) => {
  //     this.updateFlag = false;
  //     let candles = JSON.parse(message.data).prices;
  //     if (this.newWebsocket) {
  //       let newData = [];
  //       _.forEach(candles, (item) => {
  //         newData.push([item.t, item.o, item.h, item.l, item.c]);
  //       });
  //       this.websocketLastTimestamp = candles[candles.length - 1]['t'];
  //       this.chartOptions.title.text = `BTC ${this.timeframe}`
  //       this.chartOptions.series[0]['data'] = newData;
  //       this.newWebsocket = false;
  //     }
  //     else {
  //       let latestCandle = candles[candles.length - 1];
  //       if (latestCandle['t'] > this.websocketLastTimestamp) {
  //         this.chartOptions.series[0]['data'].shift();
  //         this.chartOptions.series[0]['data'].push([latestCandle['o'], latestCandle['h'], latestCandle['l'], latestCandle['c']]);
  //         this.websocketLastTimestamp = latestCandle['t']
  //       }
  //       else {
  //         this.chartOptions.series[0]['data'][-1]['o'] = latestCandle['o'];
  //         this.chartOptions.series[0]['data'][-1]['h'] = latestCandle['h'];
  //         this.chartOptions.series[0]['data'][-1]['l'] = latestCandle['l'];
  //         this.chartOptions.series[0]['data'][-1]['c'] = latestCandle['c'];
  //       }
  //     }
  //     this.updateFlag = true;
  //   };

  // }


}
