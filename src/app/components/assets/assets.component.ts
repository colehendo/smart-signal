import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import * as _ from 'lodash';


@Component({
  selector: 'app-assets',
  templateUrl: './assets.component.html',
  styleUrls: ['./assets.component.scss']
})

export class AssetsComponent implements OnInit {
  images = [944, 1011, 984].map((n) => `https://picsum.photos/id/${n}/900/500`);

  public assets: any = [
    {
      name: 'Bitcoin',
      symbol: 'BTC',
      flag: 'https://svgsilh.com/svg/722073.svg',
      price: 0
    },
    {
      name: 'Ethereum',
      symbol: 'ETH',
      flag: 'https://upload.wikimedia.org/wikipedia/commons/7/70/Ethereum_logo.svg',
      price: 0
    },
  ];

  public coins: any = [
    {
      name: 'Bitcoin',
      symbol: 'BTC',
      price: 0
    },
    {
      name: 'Ethereum',
      symbol: 'ETH',
      price: 0
    },
    {
      name: 'Litecoin',
      symbol: 'LTC',
      price: 0
    },
    {
      name: 'XRP',
      symbol: 'XRP',
      price: 0
    },
    {
      name: 'Bitcoin Cash',
      symbol: 'BCH',
      price: 0
    },
    {
      name: 'EOS',
      symbol: 'EOS',
      price: 0
    },
    {
      name: 'Tezos',
      symbol: 'XTZ',
      price: 0
    },
    {
      name: 'Bitcoin SV',
      symbol: 'BSV',
      price: 0
    },
    {
      name: 'Chainlink',
      symbol: 'LINK',
      price: 0
    },
    {
      name: 'Dash',
      symbol: 'DASH',
      price: 0
    },
  ]
  constructor(
    private http: HttpClient,
  ) {
    _.forEach(this.assets, (item) => {
      this.http.get<object>(`https://api.coinbase.com/v2/prices/${item.symbol}-USD/spot`).subscribe(data => {
        item.price = data['data']['amount'];
      })
    });
    _.forEach(this.coins, (item) => {
      this.http.get<object>(`https://api.coinbase.com/v2/prices/${item.symbol}-USD/spot`).subscribe(data => {
        item.price = data['data']['amount'];
      })
    });
  }

  ngOnInit() {
  }

}
