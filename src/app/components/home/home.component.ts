import { Component, OnInit } from '@angular/core';
import { HttpParams } from '@angular/common/http';
import * as _ from 'lodash';
import { ApiService } from '../../core/http/api.service';
import  *  as  data  from  '../../shared/modules/indicators.json';
const indicatorData: any =  (data  as  any).default;

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})

export class HomeComponent implements OnInit {

  constructor(private apiService: ApiService) { }

  private params = new HttpParams();

  cryptocurrencies = [
    { id: "BTC", price: 8656.65, change: 0.65, volume: 7300 },
    { id: "ETH", price: 8656.65, change: 0.65, volume: 7300 },
    { id: "XRP", price: 8656.65, change: 0.65, volume: 7300 },
    { id: "BCH", price: 8656.65, change: 0.65, volume: 7300 },
    { id: "XLM", price: 8656.65, change: 0.65, volume: 7300 },
    { id: "EOS", price: 8656.65, change: 0.65, volume: 7300 },
    { id: "LTC", price: 8656.65, change: 0.65, volume: 7300 },
    { id: "ADA", price: 8656.65, change: 0.65, volume: 7300 },
    { id: "XMR", price: 8656.65, change: 0.65, volume: 7300 },
    { id: "UDST", price: 8656.65, change: 0.65, volume: 7300 },
    { id: "TRX", price: 8656.65, change: 0.65, volume: 7300 },
    { id: "DASH", price: 8656.65, change: 0.65, volume: 7300 },
    { id: "MIOTA", price: 8656.65, change: 0.65, volume: 7300 },
    { id: "BNB", price: 8656.65, change: 0.65, volume: 7300 },
    { id: "NEO", price: 8656.65, change: 0.65, volume: 7300 },
  ]

  ngOnInit() {
  }

  // How to test a payload with parameters from the front end
  public payload = [];
  public timeframe = 'day';
  testParams() {
    _.forEach(indicatorData, (item) => {
      if (item.indicator === 'rsi') {
        if (this.timeframe === 'month') {
          this.payload.push({
            indicator: item.indicator,
            timeframe: 'month',
            params: item.month.params
          });
        } else if (this.timeframe === 'week') {
          this.payload.push({
            indicator: item.indicator,
            timeframe: 'week',
            params: item.month.params
          });
        } else if (this.timeframe === 'day') {
          this.payload.push({
            indicator: item.indicator,
            timeframe: 'day',
            params: item.month.params
          });
        } else if (this.timeframe === 'four_hour') {
          this.payload.push({
            indicator: item.indicator,
            timeframe: 'four_hour',
            params: item.month.params
          });
        } else if (this.timeframe === 'hour') {
          this.payload.push({
            indicator: item.indicator,
            timeframe: 'hour',
            params: item.month.params
          });
        } else if (this.timeframe === 'fifteen_minute') {
          this.payload.push({
            indicator: item.indicator,
            timeframe: 'fifteen_minute',
            params: item.month.params
          });
        } else {
          this.payload.push({
            indicator: item.indicator,
            timeframe: 'minute',
            params: item.month.params
          });
        }
      }
    });

    let all_timeframes = [];

    _.forEach(this.payload, (item) => {
      if (!all_timeframes.includes(item.timeframe)) {
        all_timeframes.push(item.timeframe);
      }
    });

    this.payload.push(all_timeframes);

    this.params = this.params.append('vals', JSON.stringify(this.payload));
    this.apiService.algorithms(this.params).subscribe(data => console.log(data));
    this.payload = [];
  }

  // How to test a custom payload
  public test_payload = [
    ['day', 'hour', 'month'],
    {indicator: 'rsi', timeframe: 'month'},
    {indicator: 'macd', timeframe: 'month'},
    {indicator: 'bb', timeframe: 'day'},
  ];

  testApi() {
    this.params = this.params.append('vals', JSON.stringify(this.test_payload));
    this.apiService.algorithms(this.params).subscribe(data => console.log(data));
  }

}
