import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AssetsComponent } from './app/components/assets/assets.component'; //Had to add this import to prevent error messages
import { HomeComponent } from './app/components/home/home.component'; //Imported for the same reason as above
import { AccountComponent } from './app/components/account/account.component';
import { AboutComponent } from './app/components/about/about.component';
import { NewsComponent } from './app/components/news/news.component';



const routes: Routes = [
	{ path:'assets', component: AssetsComponent },
	{ path:'home', component: HomeComponent },
	{ path: 'account', component: AccountComponent },
	{ path: '',   redirectTo: '/home', pathMatch: 'full' },
	{ path: 'about', component:AboutComponent },
	{ path: 'news', component:NewsComponent }
	];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
