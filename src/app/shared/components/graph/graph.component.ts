import { Component, OnInit } from '@angular/core';
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

  public btc_week = btc_week;
  public btc_month = btc_month;

  public graph_data = btc_week;

  public dataSource = {
    chart: {
      caption: "Countries With Most Oil Reserves [2017-18]",  //Set the chart caption
      subCaption: "In MMbbl = One Million barrels",  //Set the chart subcaption
      xAxisName: "Country",  //Set the x-axis name
      yAxisName: "Reserves (MMbbl)",  //Set the y-axis name
      numberSuffix: "K",
      theme: "fusion"  //Set the theme for your chart
    },
    // Chart Data - from step 2
    "data": this.graph_data
  };

  ngOnInit() {

  // testFunction() {
  //   this.graph_data = this.btc_month;
  //   console.log(this.graph_data[0])
  // }

  }
}



	// //Data will take in five parameters; [time, open, close, high ,d]
	// title="Bitcoin";
	// type="CandlestickChart";
	// data=[];
	// columnNames=['time','a','b','c','d'];