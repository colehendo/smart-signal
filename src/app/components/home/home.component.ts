import { Component, OnInit } from '@angular/core';
import { HttpParams } from '@angular/common/http';

import { IndicatorsService } from '../../core/http/indicators.service'

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  constructor(private indicatorsService: IndicatorsService) { }

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

  testApi() {
    this.params = new HttpParams();
    this.params.append('timeframe', 'day');
    this.params.append('sell_val', '70');
    this.params.append('buy_val', '30');
    this.params.append('strength_adjust', '10');
    this.indicatorsService.rsi(this.params).subscribe(data => console.log(data));
    // console.log(results);
  }

}
