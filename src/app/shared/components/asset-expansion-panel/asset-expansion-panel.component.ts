import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-asset-expansion-panel',
  templateUrl: './asset-expansion-panel.component.html',
  styleUrls: ['./asset-expansion-panel.component.scss']
})
export class AssetExpansionPanelComponent implements OnInit {

  constructor() { }

  @Input() public id: string;
  @Input() public price: string;
  @Input() public change: string;
  @Input() public volume: string;

  ngOnInit() {
  }

}
