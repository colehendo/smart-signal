import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-asset-expansion-panel',
  templateUrl: './asset-expansion-panel.component.html',
  styleUrls: ['./asset-expansion-panel.component.scss']
})
export class AssetExpansionPanelComponent implements OnInit {

  constructor() { }

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

}
