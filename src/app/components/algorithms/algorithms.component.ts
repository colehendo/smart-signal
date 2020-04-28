import { Component, OnInit } from '@angular/core';
import { HttpParams } from '@angular/common/http';
import * as _ from 'lodash';
import { switchMap } from 'rxjs/operators';

import { IndicatorsService } from '../../core/http/indicators.service';
import  *  as  data  from  '../../shared/modules/indicators.json';
const indicatorData: any =  (data  as  any).default;

import  *  as  testData  from  '../../shared/modules/indicators.json';
const testIndicatorData: any =  (testData  as  any).default;

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
    rangeSelector: {
      selected: 0
  },

  title: {
      text: 'USD to EUR exchange rate'
  },

  tooltip: {
      style: {
          width: 200
      },
      valueDecimals: 4,
      shared: true
  },

  yAxis: {
      title: {
          text: 'Exchange rate'
      }
  },

  series: [{
      name: 'USD to EUR',
      data: [],
      type: 'line',
      id: 'dataseries'

  // the event marker flags
  }, 
  {
      type: 'flags',
      data: [],
      onSeries: 'dataseries',
      shape: 'circlepin',
      width: 16
  }
]
  };

  public Highcharts: typeof Highcharts = Highcharts;
  public socket;
  public updateFlag: boolean = false;



  ngOnInit() {
    // this.chartOptions.series[0]['data'] = newData;
    console.log(window.location.href)
    let test = window.location.href
    console.log(test.split('code='))
    
  }

  get_data() {
    
    this.graph_params = this.graph_params.append('timeframes', JSON.stringify(['day', 'week']));
    this.indicatorsService.get_data(this.graph_params).subscribe(data => {
      console.log('graph data:')
      console.log(data);
      let newData = [];
      _.forEach(data[1]['tf_data'], (item) => {
        newData.push([item.t, item.c]);
      });
      this.chartOptions.series[0]['data'] = newData;
      this.updateFlag = true;
    });
  }

  combos() {
    console.log(testIndicatorData)
    let params = new HttpParams();
    params = params.set('data', JSON.stringify(testIndicatorData));
    console.log(params)
    this.indicatorsService.combinations(params).subscribe(data => {
      console.log('combo data:')
      console.log(data);
    });
  }

  public payload = [];
  public timeframe = 'day';
  public indicator = 'rsi';
  testParams() {
    this.chartOptions.series[0]['data'] = []
    this.chartOptions.series[1]['data'] = []
    _.forEach(indicatorData, (item) => {
      if (item.indicator === this.indicator) {
        let params = {}
        if (this.timeframe === 'month') { params = item.month.params; }
        else if (this.timeframe === 'week') { params = item.week.params; }
        else if (this.timeframe === 'day') { params = item.day.params; }
        else if (this.timeframe === 'four_hour') { params = item.four_hour.params; }
        else if (this.timeframe === 'hour') { params = item.hour.params; }
        else if (this.timeframe === 'fifteen_minute') { params = item.fifteen_minute.params; }
        else if (this.timeframe === 'minute') { params = item.minute.params; }

        this.payload.push({
          indicator: item.indicator,
          timeframe: this.timeframe,
          params: params
        });
      }
    });

    let all_timeframes = [];

    _.forEach(this.payload, (item) => {
      if (!all_timeframes.includes(item.timeframe)) {
        all_timeframes.push(item.timeframe);
      }
    });
    this.payload.push(all_timeframes);

    this.graph_params = this.graph_params.append('timeframes', JSON.stringify(all_timeframes));
    this.updateFlag = false;
    this.indicatorsService.get_data(this.graph_params).pipe(
      switchMap(data => {
        let newData = [];
        _.forEach(data, (timeframe) => {
          if (timeframe['timeframe'] === this.timeframe) {
            _.forEach(timeframe['tf_data'], (item) => {
              newData.push([item.t, item.c]);
            });
          }
        });
        this.chartOptions.series[0]['data'] = newData;
        return this.indicatorsService.indicators(this.alg_params)
      })).subscribe(data => {
      this.updateFlag = false;
      console.log('alg data:')
      console.log(data);
      let newData = [];
      _.forEach(data, (item) => {
        if (!!item.sig) {
          newData.push({
            x: item.time,
            title: item.sig,
            text: `Amount: ${item.amt}`
          });
        }
      });
      this.chartOptions.series[1]['data'] = newData;
    });
    this.updateFlag = true;
    this.payload = [];
  }

}
