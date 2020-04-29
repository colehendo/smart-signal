import { Component, OnInit } from '@angular/core';

interface Country {
  name: string;
  flag: string;
  area: number;
  population: number;
}



const COUNTRIES: Country[] = [
  {
    name: 'Bitcoin',
    flag: 'https://svgsilh.com/svg/722073.svg',
    area: 17075200,
    population: 146989754
  },
  {
    name: 'Ethereum',
    flag: 'https://upload.wikimedia.org/wikipedia/commons/7/70/Ethereum_logo.svg',
    area: 9976140,
    population: 36624199
  },
];
@Component({
  selector: 'app-assets',
  templateUrl: './assets.component.html',
  styleUrls: ['./assets.component.scss']
})
export class AssetsComponent implements OnInit {
  countries = COUNTRIES;
  images = [944, 1011, 984].map((n) => `https://picsum.photos/id/${n}/900/500`);

  public coins: any = [
    {
      'name': 'Bitcoin',
      'symbol': 'BTC',
      'price': 0
    },
    {
      'name': 'Ethereum',
      'symbol': 'ETH',
      'price': 0
    },
    {
      'name': 'Litecoin',
      'symbol': 'LTC',
      'price': 0
    },
    {
      'name': 'XRP',
      'symbol': 'XRP',
      'price': 0
    },
    {
      'name': 'Bitcoin Cash',
      'symbol': 'BCH',
      'price': 0
    },
    {
      'name': 'EOS',
      'symbol': 'EOS',
      'price': 0
    },
    {
      'name': 'Tezos',
      'symbol': 'XTZ',
      'price': 0
    },
    {
      'name': 'Bitcoin SV',
      'symbol': 'BSV',
      'price': 0
    },
    {
      'name': 'Chainlink',
      'symbol': 'LINK',
      'price': 0
    },
    {
      'name': 'Dash',
      'symbol': 'DASH',
      'price': 0
    },
  ]
  constructor() { }

  ngOnInit() {
  }

}
