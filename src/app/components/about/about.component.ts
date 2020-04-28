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
  public loginUrl = "https://smartsignal.auth.us-east-1.amazoncognito.com/login?client_id=62oatdg8jhsreqbobds4hp9omr&response_type=code&scope=email+openid&redirect_uri=https://www.smartsignal.watch/redirect"

  public Highcharts: typeof Highcharts = Highcharts;
  public updateFlag: boolean = false;

  public chartOptions: Highcharts.Options = {
    series: [{
      data: [],
      type: 'line'
    }]
  };

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
  ]

  constructor(
    private http: HttpClient,
    private router: Router,
    private apiService: ApiService
  ) {
    _.forEach(this.coins, (item) => {
      this.http.get<object>(`https://api.coinbase.com/v2/prices/${item.symbol}-USD/spot`).subscribe(data => {
        item.price = data['data']['amount'];
      })
    });
  }

  ngOnInit() {
    let graph_params = new HttpParams().set('table', JSON.stringify(['day']));
    this.apiService.getSingleTable(graph_params).subscribe(data => {
      this.updateFlag = false;
      let newData = [];
      _.forEach(data[0]['tf_data'], (item) => {
        console.log(item)
        newData.push([item.t, item.c]);
      });
      this.chartOptions.series[0]['data'] = newData;
      this.updateFlag = true;
    });

    if ((window.location.href).includes("localhost")) {
      this.loginUrl = "https://smartsignal.auth.us-east-1.amazoncognito.com/login?client_id=62oatdg8jhsreqbobds4hp9omr&response_type=code&scope=email+openid&redirect_uri=http://localhost:4200/redirect"
    }
  }

  buy() {
    if (localStorage.getItem('authCode')) {
      this.router.navigate(['/assets']);
    }
    else {
      window.location.href = this.loginUrl;
    }
  }

}
