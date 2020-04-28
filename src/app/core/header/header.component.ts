import { Component, OnInit, ApplicationRef } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {

  public isLoggedIn = false;

  constructor(
    private router: Router,
    private appRef: ApplicationRef
  ) { }

  public loginUrl = "https://smartsignal.auth.us-east-1.amazoncognito.com/login?client_id=62oatdg8jhsreqbobds4hp9omr&response_type=code&scope=email+openid&redirect_uri=https://www.smartsignal.watch/redirect"
  public signupUrl = "https://smartsignal.auth.us-east-1.amazoncognito.com/signup?client_id=62oatdg8jhsreqbobds4hp9omr&response_type=code&scope=email+openid&redirect_uri=https://www.smartsignal.watch/redirect"

  ngOnInit() {
    if (localStorage.getItem('authCode')) {
      this.isLoggedIn = true;
    }
    if ((window.location.href).includes("localhost")) {
      this.loginUrl = "https://smartsignal.auth.us-east-1.amazoncognito.com/login?client_id=62oatdg8jhsreqbobds4hp9omr&response_type=code&scope=email+openid&redirect_uri=http://localhost:4200/redirect"
      this.signupUrl = "https://smartsignal.auth.us-east-1.amazoncognito.com/signup?client_id=62oatdg8jhsreqbobds4hp9omr&response_type=code&scope=email+openid&redirect_uri=http://localhost:4200/redirect"
    }
  }

  home() {
    if (this.isLoggedIn) {
      this.router.navigate(['/home']);
    }
    else {
      this.router.navigate(['/']);
    }
  }

  login() {
    window.location.href = this.loginUrl;
  }

  signup() {
    window.location.href = this.signupUrl;
  }

  logout() {
    localStorage.clear();
    this.router.navigate(['/']);
  }

}
