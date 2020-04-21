import { Component, OnInit } from '@angular/core';
import { HttpParams } from '@angular/common/http';
import * as _ from 'lodash';

import { IndicatorsService } from '../../core/http/indicators.service';
import  *  as  data  from  '../../shared/modules/indicators.json';
const indicatorData: any =  (data  as  any).default;

import * as Highcharts from 'highcharts/highstock';
import HighchartsMore from 'highcharts/highcharts-more';
HighchartsMore(Highcharts);

@Component({
  selector: 'app-algorithms',
  templateUrl: './algorithms.component.html',
  styleUrls: ['./algorithms.component.scss']
})
export class AlgorithmsComponent implements OnInit {

  constructor(private indicatorsService: IndicatorsService) { }

  private alg_params = new HttpParams();
  private graph_params = new HttpParams();

  public chartOptions: Highcharts.Options = {
    series: [{
      data: [],
      type: 'candlestick'
    }],
    title:{
      text:"BTC Day"
    }
  };

  public Highcharts: typeof Highcharts = Highcharts;
  public socket;
  public candles: any;
  public updateFlag: boolean = false;



  ngOnInit() {
    // this.chartOptions.series[0]['data'] = newData;
  }

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

    this.graph_params = this.graph_params.append('timeframes', JSON.stringify(all_timeframes));
    this.indicatorsService.get_data(this.graph_params).subscribe(data => console.log(data));

    this.payload.push(all_timeframes);

    this.alg_params = this.alg_params.append('vals', JSON.stringify(this.payload));
    this.indicatorsService.indicators(this.alg_params).subscribe(data => console.log(data));
    this.payload = [];
  }

}
