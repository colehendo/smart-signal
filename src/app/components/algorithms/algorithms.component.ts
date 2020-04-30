import { Component, OnInit, ViewChild } from '@angular/core';
import { HttpParams } from '@angular/common/http';
import * as _ from 'lodash';
import { switchMap, isEmpty } from 'rxjs/operators';

import { ApiService } from '../../core/http/api.service';
import  *  as  data  from  '../../shared/modules/indicators.json';
const algorithmData: any =  (data  as  any).default;

import * as Highcharts from 'highcharts/highstock';
import HighchartsMore from 'highcharts/highcharts-more';

import {NgbTypeahead} from '@ng-bootstrap/ng-bootstrap';
import {Observable, Subject, merge} from 'rxjs';
import {debounceTime, distinctUntilChanged, filter, map} from 'rxjs/operators';

HighchartsMore(Highcharts);

@Component({
  selector: 'app-algorithms',
  templateUrl: './algorithms.component.html',
  styleUrls: ['./algorithms.component.scss']
})
export class AlgorithmsComponent implements OnInit {
  model: any;
  public catageories = [];

  constructor(private apiService: ApiService) { }

  public algorithmDropDownText = 'Select Algorithm';

  public algorithmDisplayData = algorithmData;
  public combo_params = new HttpParams().set('timeframes', '');
  public alg_params = new HttpParams().set('data', '');
  public graph_params = new HttpParams().set('data', '');

  public chartOptions: Highcharts.Options = {
    rangeSelector: {
      selected: 0
    },
    title: {
        text: `Bitcoin / U.S. Dollar: Day Candles`
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
    xAxis: { type: 'datetime' },
    series: [{
        name: 'Prices',
        data: [],
        type: 'line',
        id: 'dataseries',
        dataGrouping: {
          units: [
              [
                  'week', // unit name
                  [1] // allowed multiples
              ], [
                  'month',
                  [1, 2, 3, 4, 6]
              ]
          ]
      }
    },
    // the event marker flags
    {
        name: 'Signals',
        type: 'flags',
        data: [],
        onSeries: 'dataseries',
        shape: 'circlepin',
        width: 20
    }]
  };

  public Highcharts: typeof Highcharts = Highcharts;
  public socket;
  public updateFlag: boolean = false;

  public balance: any;
  public payload = [];
  public tableData = [];
  public combinationResults = [];
  public selectedAlgorithm: any = {};
  public algSelected = false;
  public algSelectedFromDropDown = false;
  public combinationSent = false;
  public chartPayloadSent = false;

  public timeframeOptions = [
    {
      name: '1 Month',
      value: 'month'
    },
    {
      name: '7 Days',
      value: 'week'
    },
    {
      name: '1 Day',
      value: 'day'
    },
    {
      name: '4 Hours',
      value: 'four_hour'
    },
    {
      name: '1 Hour',
      value: 'hour'
    },
    {
      name: '15 Minutes',
      value: 'fifteen_minute'
    },
    {
      name: '1 Minute',
      value: 'minute'
    }
  ];

  ngOnInit() {
    _.forEach(this.algorithmDisplayData, (item) => {
      this.catageories.push(item.name);
    })

    let graph_params = new HttpParams().set('table', JSON.stringify(['day']));
    this.apiService.getSingleTable(graph_params).subscribe(data => {
      this.updateFlag = false;
      let newData = [];
      _.forEach(data[0]['tf_data'], (item) => {
        newData.push([item.t, item.c]);
      });
      this.chartOptions.series[0]['data'] = newData;
      this.updateFlag = true;
    });
  }
  test(event){
    console.log(event);
  }

  setAlgorithm(algorithm) {
    console.log(algorithm.name)
    this.algorithmDropDownText = algorithm.name;
    this.selectedAlgorithm = algorithm;
    this.algSelectedFromDropDown = true;
  }

  appendAlgorithm(timeframe: any) {
    let params = {}
    if (timeframe.value === 'month') { params = this.selectedAlgorithm.month.params; }
    else if (timeframe.value === 'week') { params = this.selectedAlgorithm.week.params; }
    else if (timeframe.value === 'day') { params = this.selectedAlgorithm.day.params; }
    else if (timeframe.value === 'four_hour') { params = this.selectedAlgorithm.four_hour.params; }
    else if (timeframe.value === 'hour') { params = this.selectedAlgorithm.hour.params; }
    else if (timeframe.value === 'fifteen_minute') { params = this.selectedAlgorithm.fifteen_minute.params; }
    else if (timeframe.value === 'minute') { params = this.selectedAlgorithm.minute.params; }

    this.tableData.push({
      name: this.selectedAlgorithm.name,
      displayTimeframe: timeframe.name,
      algorithm: this.selectedAlgorithm.indicator,
      timeframe: timeframe.value,
      params: params
    });

    this.payload.push({
      indicator: this.selectedAlgorithm.indicator,
      timeframe: timeframe.value,
      params: params
    });
    console.log(this.payload)

    this.algorithmDropDownText = 'Select Algorithm';
    this.algSelected = true;
    this.algSelectedFromDropDown = false;
  }

  runIndividualAlgorithm(algorithm) {
    let individualPayload = [{
      indicator: algorithm.algorithm,
      timeframe: algorithm.timeframe,
      params: algorithm.params
    }]

    this.algoritmHandler(individualPayload, 'algorithm');
  }

  removeAlgFromTable(algorithm) {
    this.payload.splice(this.payload.indexOf(this.payload.find((item) => {
      return ((item.indicator === algorithm.algorithm) && (item.timeframe === algorithm.timeframe));
    })), 1);

    this.tableData.splice(this.tableData.indexOf(this.tableData.find((item) => {
      return ((item.algorithm === algorithm.algorithm) && (item.timeframe === algorithm.timeframe));
    })), 1);
    
    if (this.payload.length === 0) {
      this.algSelected = false;
    }
  }

  algoritmHandler(algorithm: any, type: string) {
    (isNaN(this.balance) || !this.balance) ? this.balance = 100000 : this.balance = parseInt(this.balance, 10);

    let all_timeframes = [];
    _.forEach(algorithm, (item) => {
      if (!all_timeframes.includes(item.timeframe)) {
        all_timeframes.push(item.timeframe);
      }
    });

    algorithm.push(all_timeframes);
    algorithm.push([this.balance]);

    type === 'algorithm' ? this.runAlgorithms(algorithm, all_timeframes) : this.runCombinations(algorithm);
  }

  runAlgorithms(algorithm: any, all_timeframes: any) {
    this.updateFlag = false;
    this.chartOptions.series[0]['data'] = []
    this.chartOptions.series[1]['data'] = []
    this.updateFlag = true;

    let algorithmTimeframe = all_timeframes[0].timeframe;

    this.graph_params = new HttpParams().set('timeframes', JSON.stringify(all_timeframes));
    this.alg_params = new HttpParams().set('data', JSON.stringify(algorithm));
    this.updateFlag = false;
    this.apiService.getData(this.graph_params).pipe(
      switchMap(data => {
        let newData = [];
        _.forEach(data[0]['tf_data'], (item) => {
          newData.push([item.t, item.c]);
        });
        this.chartOptions.series[0]['data'] = newData;
        return this.apiService.algorithms(this.alg_params)
      })).subscribe(data => {
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
        _.forEach(this.timeframeOptions, (timeframe) => {
          if (algorithmTimeframe === timeframe.value) {
            this.chartOptions.title.text = `Bitcoin / U.S. Dollar: ${timeframe.name}`;
          }
        });
        this.chartOptions.series[1]['data'] = newData;
        this.updateFlag = true;
    });
    algorithm.splice(-1,1);
  }

  runCombinations(algorithm: any) {
    console.log(algorithm)
    console.log(`params: ${this.payload}`)
    this.combinationResults.length = 0;
    this.combinationResults = [];
    console.log(this.combinationResults)
    let test = [];

    this.combo_params = new HttpParams().set('data', JSON.stringify(algorithm));
    console.log(this.combo_params)
    this.apiService.combinations(this.combo_params).subscribe(item => {
      console.log('combo data:')
      console.log(item);
      _.forEach(item, (combo) => {
        let combinationString = '';
        _.forEach(combo[0], (algorithm) => {
          _.forEach(this.algorithmDisplayData, (algorithms) => {
            if (algorithm.indicator === algorithms.indicator) {
              _.forEach(this.timeframeOptions, (timeframe) => {
                if (algorithm.timeframe === timeframe.value) {
                  combinationString = combinationString.concat(`${algorithms.name} (${timeframe.name}),\n`);
                }
              });
            }
          });
        });

        console.log(`pushing for ${combo}`)
        test.push({
          name: combinationString,
          balance: combo[1][combo[1].length - 1]['bal'],
          roi: combo[1][combo[1].length - 1]['avg_roi']
        });
        console.log(this.combinationResults)
      });
      item = [];
      item.length = 0;
      console.log(test)
    });
    this.combinationSent = true;
    algorithm.splice(-2, 2);
  }

  current_alg:string;
  get_current_alg(){
   let current_alg= this.current_alg;
   console.log("Added algorithm ",current_alg)
  }

}
