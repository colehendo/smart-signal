import { Component, OnInit } from '@angular/core';
import { btc_week } from '../../modules/btc_week';
import { btc_month } from '../../modules/btc_month';

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
  }


  testFunction() {
    this.graph_data = this.btc_month;
    console.log(this.graph_data[0])
  }

}



	// //Data will take in five parameters; [time, open, close, high ,d]
	// title="Bitcoin";
	// type="CandlestickChart";
	// data=[];
	// columnNames=['time','a','b','c','d'];