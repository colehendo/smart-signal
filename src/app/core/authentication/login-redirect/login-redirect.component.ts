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
  role = '';
 
  constructor(private navbarService: NavbarService) {
    this.navbarService.getLoginStatus().subscribe(status => this.isLoggedIn = status);
  }
  
  //Cole's original constructor function
  // constructor(
  //   private router: Router,
  // ) { }

  ngOnInit() {

    // Cole's original code 
    
    // let code = window.location.href.split('code=')[1]
    // localStorage.setItem('authCode', code);
    // this.router.navigate(['/home']);
  }

  loginUser() {
    this.navbarService.updateNavAfterAuth('user');
    this.navbarService.updateLoginStatus(true);
    this.role = 'user';
  }

}
