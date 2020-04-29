import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class NavbarService {
  private links = new Array<{ text: string, path: string }>();
  private isLoggedIn = new Subject<boolean>();

  constructor() {
    if (localStorage.getItem('authCode')) {
      this.addItem('Algorithms', 'algorithms');
      this.addItem('Account', 'account' );
      this.addItem('Assets', 'assets' );
      this.addItem('About', 'about' );
      this.addItem('News', 'news' );
      this.addItem('Logout', 'logout' );
      this.isLoggedIn.next(true);
    }
    else {
      console.log('here')
      this.addItem('Login', 'login' );
      this.addItem('Sign Up', 'signup' );
      this.isLoggedIn.next(false);
    }
  }
  addItem(text, path) {
    this.links.push({ text: text, path: path });
  }

  getLinks() {
    return this.links;
  }
 
  getLoginStatus() {
    return this.isLoggedIn;
  }

  updateLoginStatus(status: boolean) {
    this.isLoggedIn.next(status);
    this.links.length = 0;
 
    if (!status) {
      localStorage.clear();
      this.addItem('Login', 'login');
      this.addItem('Sign Up', 'signup');
    }
    else {
      this.addItem('Algorithms', 'algorithms');
      this.addItem('Account', 'account');
      this.addItem('Assets', 'assets');
      this.addItem('About', 'about');
      this.addItem('News', 'news');
      this.addItem('Logout', 'logout');
    }
  }
  
  removeItem({ text }) {
    this.links.forEach((link, index) => {
      if (link.text === text) {
        this.links.splice(index, 1);
      }
    });
  }
}
