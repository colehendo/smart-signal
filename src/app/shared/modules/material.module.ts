import { NgModule } from '@angular/core';
import { MatExpansionModule, MatChipsModule, MatCardModule } from '@angular/material';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

@NgModule({
    declarations: [],
    imports: [
        BrowserAnimationsModule,
        MatExpansionModule,
        MatChipsModule,
        MatCardModule
    ],
    exports: [
        BrowserAnimationsModule,
        MatExpansionModule,
        MatChipsModule,
        MatCardModule
    ],
    providers: [ ]
})
export class MaterialModule { }
