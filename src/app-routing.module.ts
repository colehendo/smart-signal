import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AssetsComponent } from './app/components/assets/assets.component'; //Had to add this import to prevent error messages
import { HomeComponent } from './app/components/home/home.component'; //Imported for the same reason as above
import { AccountComponent } from './app/components/account/account.component';
import { AboutComponent } from './app/components/about/about.component';
import { AlgorithmsComponent } from './app/components/algorithms/algorithms.component';
import { NewsComponent } from './app/components/news/news.component';
import { LandingPageComponent } from './app/components/landing-page/landing-page.component';
import { PageNotFoundComponent } from './app/components/page-not-found/page-not-found.component';



const routes: Routes = [
	{ path: '', component: LandingPageComponent },
	{ path: 'about', component: AboutComponent },
	{ path: 'account', component: AccountComponent },
	{ path: 'algorithms', component: AlgorithmsComponent },
	{ path: 'assets', component: AssetsComponent },
	{ path: 'home', component: HomeComponent },
	{ path: 'news', component: NewsComponent },
  	{ path: '**', component: PageNotFoundComponent }
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes, { scrollPositionRestoration: 'enabled' })
  ],
  exports: [RouterModule]
})
export class AppRoutingModule { }
