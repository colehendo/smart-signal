import { Component, OnInit } from '@angular/core';
import { HttpParams } from '@angular/common/http';
import * as _ from 'lodash';
import { switchMap } from 'rxjs/operators';

import { ApiService } from '../../core/http/api.service';
import  *  as  data  from  '../../shared/modules/indicators.json';
const indicatorData: any =  (data  as  any).default;

import  *  as  testData  from  '../../shared/modules/test-indicators.json';
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

  constructor(private apiService: ApiService) { }

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
      name: 'BTC',
      data: [],
      type: 'line',
      id: 'dataseries'

  // the event marker flags
  }, 
  },
  {
      type: 'flags',
      data: [],
      onSeries: 'dataseries',
      shape: 'circlepin',
      width: 20
  }
]
  };

  public Highcharts: typeof Highcharts = Highcharts;
  public socket;
  public updateFlag: boolean = false;

  ngOnInit() { }

  getData() {
    let graph_params = new HttpParams().set('timeframes', JSON.stringify(['day', 'week']));
    this.apiService.getData(graph_params).subscribe(data => {
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

  search = (text$: Observable<string>) => {
    const debouncedText$ = text$.pipe(debounceTime(200), distinctUntilChanged());
    const clicksWithClosedPopup$ = this.click$.pipe(filter(() => !this.instance.isPopupOpen()));
    const inputFocus$ = this.focus$;

    return merge(debouncedText$, inputFocus$, clicksWithClosedPopup$).pipe(
      map(term => (term === '' ? categories
        : categories.filter(v => v.toLowerCase().indexOf(term.toLowerCase()) > -1)).slice(0, 10))
    );
  }

  combos() {
    console.log(testIndicatorData)
    let combo_params = new HttpParams().set('data', JSON.stringify(testIndicatorData));
    console.log(combo_params)
    this.apiService.combinations(combo_params).subscribe(data => {
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

    let graph_params = new HttpParams().set('timeframes', JSON.stringify(all_timeframes));
    let alg_params = new HttpParams().set('vals', JSON.stringify(this.payload));
    this.updateFlag = false;
    this.apiService.getData(graph_params).pipe(
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
        return this.apiService.algorithms(alg_params)
      })).subscribe(data => {
        console.log('alg data:')
        console.log(data);
        let newData = [];
        _.forEach(data, (item) => {
          if (!!item.sig) {
            newData.push({
              x: new Date(item.time),
              title: item.sig.toUpperCase(),
              text: `Amount: $${item.amt.toFixed(2)}`
            });
          }
        });
        this.chartOptions.series[1]['data'] = newData;
        this.updateFlag = true;
        this.payload = [];
    });
  }

}
