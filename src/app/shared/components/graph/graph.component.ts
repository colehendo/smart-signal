import { Component, OnInit } from '@angular/core';
import { btc_week } from '../../modules/btc_week';
import { btc_month } from '../../modules/btc_month';
import * as FusionCharts from 'fusioncharts';

@Component({
  selector: 'app-graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.scss']
})


export class GraphComponent implements OnInit {

  constructor(
  ) { }

  public btc_week = btc_week;
  public btc_month = btc_month;

  public graph_data = btc_week;

  public chartObj = new FusionCharts({
    type: 'candlestick',
    renderAt: 'chart-container',
    width: '680',
    height: '390',
    dataFormat: 'json',
    dataSource: {
      chart: {
        theme: "fusion",
        caption: "Daily Stock Price HRYS",
        subCaption: "Last 2 months",
        numberprefix: "$",
        vNumberPrefix: " ",
        pyaxisname: "Price",
        vyaxisname: "Volume (In Millions)",
        toolTipColor: "#ffffff",
        toolTipBorderThickness: "0",
        toolTipBgColor: "#000000",
        toolTipBgAlpha: "80",
        toolTipBorderRadius: "2",
        toolTipPadding: "5"
      },
      categories: [
          {
              category: [
                  {
                      label: "2 month ago",
                      x: "1"
                  },
                  {
                      label: "1 month ago",
                      x: "31"
                  },
                  {
                      label: "Today",
                      x: "60"
                  }
              ]
          }
      ],
      // Chart Data - from step 2
      dataset: [
        {
          data: this.graph_data
        }
      ]
    }
  });

  ngOnInit() {

    console.log('single btc month:');
    console.log(this.btc_month[0])

    console.log('bitcoin month:');
    for (let i = 0; i < 10; i++){
      console.log(this.btc_month[i]);
      // console.log(JSON.stringify(this.btc_month[i]));
    }

    console.log('exact results:');
    console.log(this.btc_month[0].Date)
    console.log(this.btc_month[0].Price)
    console.log(this.btc_month[0].Open)
    console.log(this.btc_month[0].High)
    console.log(this.btc_month[0].Low)
    console.log(this.btc_month[0]["Vol."])
    console.log(this.btc_month[0]["Change %"])
    
    console.log(this.graph_data[0])

    this.chartObj.render();
  }


  testFunction() {
    this.chartObj.render();
    this.graph_data = this.btc_month;
    console.log(this.graph_data[0])
  }

}



	// //Data will take in five parameters; [time, open, close, high ,d]
	// title="Bitcoin";
	// type="CandlestickChart";
	// data=[];
	// columnNames=['time','a','b','c','d'];