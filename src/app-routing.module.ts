import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AssetsComponent } from './app/components/assets/assets.component'; //Had to add this import to prevent error messages
import { HomeComponent } from './app/components/home/home.component'; //Imported for the same reason as above
import { AccountComponent } from './app/components/account/account.component';
import { AboutComponent } from './app/components/about/about.component';
import { AlgorithmsComponent } from './app/components/algorithms/algorithms.component';
import { LandingPageComponent } from './app/components/landing-page/landing-page.component'
import { NewsComponent } from './app/components/news/news.component';
import { LoginRedirectComponent } from './app/core/authentication/login-redirect/login-redirect.component';
import { PageNotFoundComponent } from './app/components/page-not-found/page-not-found.component';

import { RoleGuard } from './app/core/guards/role.guard';

import { Router } from '@angular/router';

const routes: Routes = [
	{ path: '', component: LandingPageComponent },
	{ path: 'redirect', component: LoginRedirectComponent },
	{
		path: 'about',
		component: AboutComponent,
		canActivate: [ RoleGuard ],
	},
	{
		path: 'account',
		component: AccountComponent,
		canActivate: [ RoleGuard ],
	},
	{
		path: 'algorithms',
		component: AlgorithmsComponent,
		canActivate: [ RoleGuard ],
	},
	{
		path: 'assets',
		component: AssetsComponent,
		canActivate: [ RoleGuard ],
	},
	{
		path: 'home',
		component: HomeComponent,
		canActivate: [ RoleGuard ],
	},
	{
		path: 'news',
		component: NewsComponent,
	},
  	{ path: '**', component: PageNotFoundComponent }
];


@NgModule({

  imports: [
    RouterModule.forRoot(routes, { scrollPositionRestoration: 'enabled' })
  ],
  exports: [RouterModule],
  entryComponents: [
    AboutComponent,
    LoginRedirectComponent,
    NewsComponent
  ],
  declarations:[
	// LandingPageComponent,
	// LoginRedirectComponent,
	// AboutComponent,
	// AccountComponent,
	// AlgorithmsComponent,
	// AssetsComponent,
	// HomeComponent,
	// NewsComponent
  ]
})
export class AppRoutingModule { 
	links: Array<{ text: string, path: string }>;
	constructor(private router: Router) {
		this.router.config.unshift(
		  { path: 'about', component: AboutComponent },
		  { path: 'login', component: LoginRedirectComponent },
		  { path: 'news', component: NewsComponent },
		);
	  }
}


