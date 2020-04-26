import { Component, OnInit } from '@angular/core';

const loginURL = "https://smartsignal.auth.us-east-1.amazoncognito.com/login?client_id=62oatdg8jhsreqbobds4hp9omr&response_type=code&scope=email+openid&redirect_uri=https://www.smartsignal.watch/home";
const signupURL = "https://smartsignal.auth.us-east-1.amazoncognito.com/signup?client_id=62oatdg8jhsreqbobds4hp9omr&response_type=code&scope=email+openid&redirect_uri=https://www.smartsignal.watch/home";

@Component({
  selector: 'app-landing-page',
  templateUrl: './landing-page.component.html',
  styleUrls: ['./landing-page.component.scss']
})
export class LandingPageComponent implements OnInit {

  constructor() { }

  ngOnInit() {
  }
}
