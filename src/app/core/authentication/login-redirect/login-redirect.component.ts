import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { NavbarService } from '../../../services/navbar.service';

@Component({
  selector: 'app-login-redirect',
  templateUrl: './login-redirect.component.html',
  styleUrls: ['./login-redirect.component.scss']
})
export class LoginRedirectComponent implements OnInit {

  isLoggedIn = false;
 
  constructor(
    private router: Router,
    private navbarService: NavbarService
  ) {
    this.navbarService.getLoginStatus().subscribe(status => this.isLoggedIn = status);
  }

  ngOnInit() {
    if ((window.location.href).includes('code=')) {
      let code = window.location.href.split('code=')[1]
      localStorage.setItem('authCode', code);
      this.navbarService.updateNavAfterAuth();
      this.navbarService.updateLoginStatus(true);
    }
    this.router.navigate(['/home']);
  }
}
