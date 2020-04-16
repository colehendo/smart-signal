import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';

import ReconnectingWebSocket from 'reconnecting-websocket';

import { AppRoutingModule } from './app-routing.module';
import { HeaderComponent } from './app/core/header/header.component';
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
import { LandingPageComponent } from './app/components/landing-page/landing-page.component';
import { PageNotFoundComponent } from './app/components/page-not-found/page-not-found.component';

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
    NewsComponent,
    LandingPageComponent,
    PageNotFoundComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    MaterialModule,
    HighchartsChartModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
