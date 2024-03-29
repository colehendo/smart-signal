import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Router } from '@angular/router';
import * as _ from 'lodash';
import { ApiService } from '../../core/http/api.service';

import * as Highcharts from 'highcharts/highstock';
import HighchartsMore from 'highcharts/highcharts-more';
HighchartsMore(Highcharts);

@Component({
  selector: 'app-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.scss']
})
export class AboutComponent implements OnInit {
  public loginUrl = "https://smartsignal.auth.us-east-1.amazoncognito.com/login?client_id=62oatdg8jhsreqbobds4hp9omr&response_type=code&scope=email+openid&redirect_uri=https://www.smartsignal.watch/redirect";
  public loggedIn = false;

  public Highcharts: typeof Highcharts = Highcharts;
  public updateFlag: boolean = false;

  public chartOptions: Highcharts.Options = {
    chart: {
      zoomType: 'x',
      panKey: 'shift',
      scrollablePlotArea: {
          minWidth: 600
      }
    },
    title: {
        text: `Bitcoin (USD)`
    },
    // credits: {
    //     enabled: false
    // },
    
    xAxis: {
        type: 'datetime',
    },
    yAxis: {
        startOnTick: true,
        endOnTick: false,
        maxPadding: 0.35,
        title: {
            text: 'Price (USD)'
        },
        labels: {
            format: '${value}'
        }
    },
    tooltip: {
      pointFormat: 'Price: ${point.y}',
      shared: true
    },

    // legend: {
    //     enabled: false
    // },
    plotOptions: {
      area: {
          lineColor: '#00D080',
          fillColor: {
              linearGradient: {
                  x1: 0,
                  y1: 0,
                  x2: 0,
                  y2: 2
              },
              stops: [
                  [0, '#00D080'],
                  [1, '#4C4C4B']
              ]
          },
          marker: {
              radius: 2
          },
          lineWidth: 1,
          states: {
              hover: {
                  lineWidth: 1
              }
          },
          threshold: null
      }
  },
    series: [
      {
        name: 'BTC Price (USD)',
        data: [],
        type: 'area',
        id: 'prices'
      }
    ]
  };

  

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
    private router: Router,
    private apiService: ApiService
  ) {
    if (localStorage.getItem('authCode')) {
      this.loggedIn = true;
    }
    _.forEach(this.coins, (item) => {
      this.http.get<object>(`https://api.coinbase.com/v2/prices/${item.symbol}-USD/spot`).subscribe(data => {
        item.price = data['data']['amount'];
      })
    });
  }
  ngAfterViewInit() {
    // @ts-ignore
    twttr.widgets.load();
  }

  ngOnInit() {
    let graph_params = new HttpParams().set('table', JSON.stringify(['day']));
    this.apiService.getSingleTable(graph_params).subscribe(data => {
      this.updateFlag = false;
      let newData = [];
      _.forEach(data[0]['tf_data'], (item) => {
        newData.push([item.t * 1000, item.c]);
      });
      this.chartOptions.series[0]['data'] = newData;
      this.updateFlag = true;
    });

    if ((window.location.href).includes("localhost")) {
      this.loginUrl = "https://smartsignal.auth.us-east-1.amazoncognito.com/login?client_id=62oatdg8jhsreqbobds4hp9omr&response_type=code&scope=email+openid&redirect_uri=http://localhost:4200/redirect"
    }
    let twitter_params = new HttpParams().set('q', JSON.stringify('bitcoin'));
    this.http.get<object>(`https://api.twitter.com/1.1/search/tweets.json`, {params: twitter_params}).subscribe(data => {
      console.log(data)
    })
  }

  buy() {
    if (this.loggedIn) {
      this.router.navigate(['/assets']);
    }
    else {
      window.location.href = this.loginUrl;
    }
  }

}
