import { Component, OnInit } from '@angular/core';
import ReconnectingWebSocket from 'reconnecting-websocket';
import { btc_week } from '../../modules/btc_week';
import { btc_month } from '../../modules/btc_month';

import * as Highcharts from 'highcharts';
import HighchartsMore from 'highcharts/highcharts-more';
HighchartsMore(Highcharts);


@Component({
  selector: 'app-graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.scss']
})


export class GraphComponent implements OnInit {
  public Highcharts: typeof Highcharts = Highcharts;
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
    public chartOptions: Highcharts.Options = {
      series: [{
        data: [
          [760, 801, 848, 895, 965],
          [733, 853, 939, 980, 1080],
          [714, 762, 817, 870, 918],
          [724, 802, 806, 871, 950],
          [834, 836, 864, 882, 910],
          [600, 702,795, 849, 971],
          [760, 801, 848, 895, 965],
          [733, 853, 939, 980, 1080],
          [714, 762, 817, 870, 918],
          [724, 802, 806, 871, 950],
          [834, 836, 864, 882, 910],
          [600, 702,795, 849, 971],
          [760, 801, 848, 895, 965],
          [733, 853, 939, 980, 1080],
          [714, 762, 817, 870, 918],
          [724, 802, 806, 871, 950],
          [834, 836, 864, 882, 910],
          [600, 702,795, 849, 971],
          [760, 801, 848, 895, 965],
          [799, 953, 1039, 980, 1080],
          [714, 762, 817, 870, 918],
          [724, 802, 806, 871, 950],
          [834, 836, 864, 882, 910],
          [600, 702,795, 849, 971],
        ],
        type: 'boxplot'
      }]
    };

  constructor(
  ) { }

  

}
