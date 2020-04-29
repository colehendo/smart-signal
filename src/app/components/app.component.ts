import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { AssetsComponent } from './assets/assets.component'; //Had to add this import to prevent error messages
import { HomeComponent } from './home/home.component'; //Imported for the same reason as above
import { AccountComponent } from './account/account.component';
import { AboutComponent } from './about/about.component';
import { AlgorithmsComponent } from './algorithms/algorithms.component';
import { LandingPageComponent } from './landing-page/landing-page.component'
import { NewsComponent } from './news/news.component';
import { LoginRedirectComponent } from '../core/authentication/login-redirect/login-redirect.component';
import { PageNotFoundComponent } from './page-not-found/page-not-found.component';
import { NavbarService } from '../services/navbar.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'smart-signal';
  // links: Array<{ text: string, path: string }>;
  // isLoggedIn = false;

  // constructor(private router: Router, private navbarService: NavbarService) {
  //   this.router.config.unshift(
  //     { path: 'login', component: LoginRedirectComponent },
  //     { path: 'news', component: NewsComponent },
  //     { path: '', component: AboutComponent },
  //   );
  // }
  // ngOnInit(){
  //   this.links = this.navbarService.getLinks();
  //   this.navbarService.getLoginStatus().subscribe(status => this.isLoggedIn = status);
  // }

  // logout() {
  //   this.navbarService.updateLoginStatus(false);
  //   this.router.navigate(['home']);
  // }
  //Commented out dynamic navbar typescript
}


