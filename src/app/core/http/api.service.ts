import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  constructor(private http: HttpClient) {}

  public baseUrl = 'https://rwd7t69k41.execute-api.us-east-1.amazonaws.com/prod';

  algorithms(params: HttpParams): Observable<any> {
    console.log(params)
    return this.http.get<object>(`${this.baseUrl}/algorithms`, {params: params});
  }

  getData(params: HttpParams): Observable<any> {
    return this.http.get<object>(`${this.baseUrl}/get-data`, {params: params});
  }

  getSingleTable(params: HttpParams): Observable<any> {
    return this.http.get<object>(`${this.baseUrl}/get-single-table`, {params: params});
  }

  combinations(params: HttpParams): Observable<any> {
    return this.http.get<object>(`${this.baseUrl}/combinations`, {params: params});
  }

  maxProfit(params: HttpParams): Observable<any> {
    console.log('getting the thing')
    return this.http.get<object>(`${this.baseUrl}/find-max-profit`, {params: params});
  }

  getPrice(param: string): Observable<any> {
    return this.http.get<object>(`https://api.coinbase.com/v2/prices/${param}-USD/spot`);
  }
}
