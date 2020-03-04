import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { HeaderComponent } from './app/core/header/header.component';

import { FusionChartsModule } from 'angular-fusioncharts';

import * as FusionCharts from 'fusioncharts';
import * as charts from 'fusioncharts/fusioncharts.charts';
import * as FusionTheme from 'fusioncharts/themes/fusioncharts.theme.fusion';

// Pass the fusioncharts library and chart modules
FusionChartsModule.fcRoot(FusionCharts, charts, FusionTheme);

import { AppComponent } from './app/components/app.component';
import { HomeComponent } from './app/components/home/home.component';
import { AssetsComponent } from './app/components/assets/assets.component';
import { AccountComponent } from './app/components/account/account.component';
import { AboutComponent } from './app/components/about/about.component';
import { NewsComponent } from './app/components/news/news.component'; //Added this line from original branch

import { AssetExpansionPanelComponent } from './app/shared/components/asset-expansion-panel/asset-expansion-panel.component';
import { MaterialModule } from './app/shared/modules/material.module';
import { GraphComponent } from './app/shared/components/graph/graph.component'; //Added from here down
import { HighchartsChartModule } from 'highcharts-angular';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    AssetExpansionPanelComponent,
    HomeComponent,
    GraphComponent,
    AssetsComponent,
    AccountComponent,
    AboutComponent,
    NewsComponent //Added graph component to declaration
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    MaterialModule,
    FusionChartsModule,
    HighchartsChartModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
