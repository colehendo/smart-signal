import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AssetExpansionPanelComponent } from './asset-expansion-panel.component';

describe('AssetExpansionPanelComponent', () => {
  let component: AssetExpansionPanelComponent;
  let fixture: ComponentFixture<AssetExpansionPanelComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AssetExpansionPanelComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AssetExpansionPanelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
