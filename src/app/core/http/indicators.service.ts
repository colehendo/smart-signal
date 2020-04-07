import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class IndicatorsService {

  constructor(private http: HttpClient) {}


  public baseUrl = 'https://rwd7t69k41.execute-api.us-east-1.amazonaws.com/prod';

  indicators(params: HttpParams): Observable<any> {
    return this.http.get<object>(`${this.baseUrl}/indicators`, {params: params});
  }
}
