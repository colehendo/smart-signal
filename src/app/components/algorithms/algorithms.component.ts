import { Component, OnInit } from '@angular/core';
import { HttpParams } from '@angular/common/http';
import * as _ from 'lodash';
import { switchMap } from 'rxjs/operators';

import { ApiService } from '../../core/http/api.service';
import  *  as  data  from  '../../shared/modules/indicators.json';
const algorithmData: any =  (data  as  any).default;

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

  public algorithmDropDownText = 'Select Algorithm';
  public algorithmDisplayData = algorithmData;
  public combo_params = new HttpParams().set('timeframes', '');
  public alg_params = new HttpParams().set('data', '');
  public graph_params = new HttpParams().set('data', '');

  public chartOptions: Highcharts.Options = {
    chart: {
      zoomType: 'x',
      panKey: 'shift',
      scrollablePlotArea: {
          minWidth: 600
      }
    },
    title: {
        text: `Bitcoin (USD): Day Datapoints`
    },
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
    plotOptions: {
      area: {
          lineColor: '#00D080',
          fillOpacity: 0, 
          marker: {
              radius: 3
          },
          lineWidth: 3,
          states: {
              hover: {
                  lineWidth: 2
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
      },
        {
          type: 'flags',
          name: 'Signals',
          data: [],
          onSeries: 'prices',
          shape: 'squarepin',
          width: 16
      }
    ]
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
    this.algorithmDisplayData.sort((a, b) => a.indicator.localeCompare(b.indicator));

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
  }

  setAlgorithm(algorithm) {
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
    this.chartOptions.series[0]['data'] = [];
    this.chartOptions.series[1]['data'] = [];
    this.updateFlag = true;

    this.graph_params = new HttpParams().set('timeframes', JSON.stringify(all_timeframes));
    this.alg_params = new HttpParams().set('data', JSON.stringify(algorithm));
    this.updateFlag = false;
    this.apiService.getData(this.graph_params).pipe(
      switchMap(data => {
        let newData = [];
        _.forEach(data[0]['tf_data'], (item) => {
          newData.push([item.t * 1000, item.c]);
        });
        this.chartOptions.series[0]['data'] = newData;
        return this.apiService.algorithms(this.alg_params)
      })).subscribe(data => {
        console.log(`alg data: ${data}`)
        let flags = []

        _.forEach(data, (item) => {
          if (item.sig) {
            flags.push({
              x: new Date(item.time * 1000),
              title: item.sig,
              text: `Transaction: $${item.amt.toFixed(2)}`,
            })
          }
        });
        _.forEach(this.timeframeOptions, (timeframe) => {
          if (all_timeframes.includes(timeframe.value)) {
            console.log('found it')
            this.chartOptions.title.text = `Bitcoin (USD): ${timeframe.name} Datapoints`;
            this.chartOptions.series[1]['data'] = flags;
            console.log(this.chartOptions.annotations)
            this.updateFlag = true;
            return false;
          }
        });
    });
    algorithm.splice(-1,1);
  }

  runCombinations(algorithm: any) {
    this.combinationResults = [];

    this.combo_params = new HttpParams().set('data', JSON.stringify(algorithm));
    this.apiService.combinations(this.combo_params).subscribe(item => {
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

        this.combinationResults.push({
          name: combinationString,
          balance: combo[1][combo[1].length - 1]['bal'],
          roi: combo[1][combo[1].length - 1]['avg_roi']
        });
      });
      this.combinationResults.sort((a, b) => a.roi + b.roi);
    });
    this.combinationSent = true;
    algorithm.splice(-2, 2);
  }
}
