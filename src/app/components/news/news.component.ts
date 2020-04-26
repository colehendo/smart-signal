import { Component, OnInit } from '@angular/core';
import {ViewChild} from '@angular/core';
import {NgbTypeahead} from '@ng-bootstrap/ng-bootstrap';
import {Observable, Subject, merge} from 'rxjs';
import {debounceTime, distinctUntilChanged, filter, map} from 'rxjs/operators';


const categories=["Bitcoin","Ethereum", "DogeCoin", "Cryptocurrency","Coronavirus","Blockchain","Ripple", "OMG", "NEO","BAT"]
@Component({
  selector: 'app-news',
  templateUrl: './news.component.html',
  styleUrls: ['./news.component.scss']
})
export class NewsComponent implements OnInit {

  // images = [944, 1011, 984].map((n) => `https://picsum.photos/id/${n}/900/500`);
  images = [
    "https://g.foolcdn.com/editorial/images/469220/a-chart-with-the-names-of-several-cryptocurrencies-in-the-background-with-a-graph-moving-up.jpg",
    "https://g.foolcdn.com/editorial/images/486290/gettyimages-826058232.jpg",
    "https://cybermashup.files.wordpress.com/2017/10/istock-621921512.jpg"
  ]

  model: any;

  @ViewChild('instance', {static: true}) instance: NgbTypeahead;
  focus$ = new Subject<string>();
  click$ = new Subject<string>();

  search = (text$: Observable<string>) => {
    const debouncedText$ = text$.pipe(debounceTime(200), distinctUntilChanged());
    const clicksWithClosedPopup$ = this.click$.pipe(filter(() => !this.instance.isPopupOpen()));
    const inputFocus$ = this.focus$;

    return merge(debouncedText$, inputFocus$, clicksWithClosedPopup$).pipe(
      map(term => (term === '' ? categories
        : categories.filter(v => v.toLowerCase().indexOf(term.toLowerCase()) > -1)).slice(0, 10))
    );
  }

  constructor() { }

  ngOnInit() {
  }

}
