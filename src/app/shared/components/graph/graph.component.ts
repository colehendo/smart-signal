import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.scss']
})


export class GraphComponent implements OnInit {

  constructor() { }

  ngOnInit() {
  }

}



	// //Data will take in five parameters; [time, open, close, high ,d]
	// title="Bitcoin";
	// type="CandlestickChart";
	// data=[];
	// columnNames=['time','a','b','c','d'];