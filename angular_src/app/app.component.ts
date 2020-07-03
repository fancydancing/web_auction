import { Component, OnInit } from '@angular/core';
import { HelpersService } from './helpers/helpers.service';

@Component({
  selector: 'app-root',
  templateUrl: 'app.component.html',
  styles: []
})
export class AppComponent implements OnInit {
    logged: Boolean = false;

    is_admin: boolean = false;

    constructor(public helpersService: HelpersService) { }

    ngOnInit() {
        this.is_admin = this.helpersService.isAdmin();
    }

    onSignInEvent(ev: String) {
        if (ev = 'logged') {
            this.logged = true;
        }
    }
}
