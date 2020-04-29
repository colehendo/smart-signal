import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class NavbarService {
  private links = new Array<{ text: string, path: string }>();
  private isLoggedIn = new Subject<boolean>();

  constructor() { 
    this.addItem({ text: 'Login', path: 'login' });
    this.addItem({ text: 'Sign Up', path: 'signup' });
    this.isLoggedIn.next(false);
  }
  addItem({ text, path }) {
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
 
    if (!status) {
      this.clearAllItems();
      this.addItem({ text: 'Login', path: 'login' });
      this.addItem({ text: 'Sign Up', path: 'signup' });
    }
  }
  
  removeItem({ text }) {
    this.links.forEach((link, index) => {
      if (link.text === text) {
        this.links.splice(index, 1);
      }
    });
  }
 
  clearAllItems() {
    this.links.length = 0;
    localStorage.clear();
  }

  updateNavAfterAuth(): void {
    this.removeItem({ text: 'Login' });
    this.removeItem({ text: 'Sign Up' });
 
    this.addItem({ text: 'Algorithms', path: 'algorithms' });
    this.addItem({ text: 'Account', path: 'account' });
    this.addItem({ text: 'Assets', path:'assets' });
    this.addItem({ text: 'About', path: 'about' });
    this.addItem({ text: 'News', path: 'news' });
    this.addItem({ text: 'Logout', path: 'logout' });
  }
  
}
