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

  public btc_week = btc_week;
  public btc_month = btc_month;
  public graph_data = btc_week;

  public Highcharts: typeof Highcharts = Highcharts;
  public chartOptions: Highcharts.Options = {
    series: [{
      data: [
        [760, 801, 848, 895, 965],
        [733, 853, 939, 980, 1080],
        [714, 762, 817, 870, 918],
        [724, 802, 806, 871, 950],
        [834, 836, 864, 882, 910]
      ],
      type: 'boxplot'
    }]
  };

  constructor( ) {
    // this.options = {
    //   chart: { type: 'item' },
    //   title : { text : 'simple chart' },
    //   series: [{
    //       data: [29.9, 71.5, 106.4, 129.2],
    //   }]
    // };
  }

  ngOnInit() {
  }

}