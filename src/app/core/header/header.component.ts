import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { AssetsComponent } from '../../components/assets/assets.component'; //Had to add this import to prevent error messages
import { HomeComponent } from '../../components/home/home.component'; //Imported for the same reason as above
import { AccountComponent } from '../../components/account/account.component';
import { AboutComponent } from '../../components/about/about.component';
import { AlgorithmsComponent } from '../../components/algorithms/algorithms.component';
import { LandingPageComponent } from '../../components/landing-page/landing-page.component'
import { NewsComponent } from '../../components/news/news.component';
import { LoginRedirectComponent } from '../authentication/login-redirect/login-redirect.component';
import { PageNotFoundComponent } from '../../components/page-not-found/page-not-found.component';
import { NavbarService } from '../../shared/services/navbar.service';

import { RoleGuard } from '../guards/role.guard';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {

  public isLoggedIn = false;
  public loginUrl = "https://smartsignal.auth.us-east-1.amazoncognito.com/login?client_id=62oatdg8jhsreqbobds4hp9omr&response_type=code&scope=email+openid&redirect_uri=https://www.smartsignal.watch/redirect"
  public signupUrl = "https://smartsignal.auth.us-east-1.amazoncognito.com/signup?client_id=62oatdg8jhsreqbobds4hp9omr&response_type=code&scope=email+openid&redirect_uri=https://www.smartsignal.watch/redirect"

  links: Array<{ text: string, path: string }>;

  constructor(
    private router: Router,
    private navbarService: NavbarService
  ) {
    this.router.config.unshift(
      // { path: 'login', component: LoginRedirectComponent },
      { path: 'home', component: HomeComponent, canActivate: [ RoleGuard ] },
      { path: 'news', component: NewsComponent },
      { path: 'about', component: AboutComponent, canActivate: [ RoleGuard ] },
      { path: 'account', component: AccountComponent, canActivate: [ RoleGuard ] },
      { path: 'assets', component: AssetsComponent, canActivate: [ RoleGuard ] },
      { path: 'algorithms', component: AlgorithmsComponent, canActivate: [ RoleGuard ] }
    );
  }

  ngOnInit() {
    if (localStorage.getItem('authCode')) {
      this.isLoggedIn = true;
    }
    if ((window.location.href).includes("localhost")) {
      this.loginUrl = "https://smartsignal.auth.us-east-1.amazoncognito.com/login?client_id=62oatdg8jhsreqbobds4hp9omr&response_type=code&scope=email+openid&redirect_uri=http://localhost:4200/redirect"
      this.signupUrl = "https://smartsignal.auth.us-east-1.amazoncognito.com/signup?client_id=62oatdg8jhsreqbobds4hp9omr&response_type=code&scope=email+openid&redirect_uri=http://localhost:4200/redirect"
    }

    this.links = this.navbarService.getLinks();
    this.navbarService.getLoginStatus().subscribe(status => this.isLoggedIn = status);
    
  }

  reroute(path) {
    console.log(path)
    if (path === 'login') {
      window.location.href = this.loginUrl;
    }
    else if (path === 'signup') {
      window.location.href = this.signupUrl;
    }
    else if (path === 'logout') {
      this.navbarService.updateLoginStatus(false);
      this.router.navigate(['/']);
    }
    else {
      this.router.navigate([`/${path}`])
    }
  }

}
