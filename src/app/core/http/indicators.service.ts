import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class IndicatorsService {

  constructor(private http: HttpClient) {}


  public baseUrl = 'https://rwd7t69k41.execute-api.us-east-1.amazonaws.com/prod';
  public shit = [
    ['day', 'hour', 'month'],
    {indicator: 'rsi', timeframe: 'day'},
    {indicator: 'macd', timeframe: 'hour'},
    {indicator: 'bb', timeframe: 'month'},
  ]

  rsi(params: HttpParams): Observable<any> {
    let param = new HttpParams();
    param = param.append('vals', JSON.stringify(this.shit));

    // return this.httpClient.get("http://server.com/api/products", {params: params});
    // return this.http.get<object>(`${this.baseUrl}/rsi`, { params: params });
    return this.http.get<object>(`${this.baseUrl}/indicators`, {params: param});
  }
}
