import { Component, OnInit } from '@angular/core';
import { btc_week } from '../../modules/btc_week';
import { btc_month } from '../../modules/btc_month';


@Component({
  selector: 'app-graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.scss']
})


export class GraphComponent implements OnInit {

  public btc_week = btc_week;
  public btc_month = btc_month;
  public graph_data = btc_week;

  public options: Object;
  public chart : Object;

  constructor( ) {
    this.options = {
      chart: { type: 'box_plot' },
      title : { text : 'simple chart' },
      series: [{
          data: [29.9, 71.5, 106.4, 129.2],
      }]
    };
  }

  ngOnInit() {
  }

}