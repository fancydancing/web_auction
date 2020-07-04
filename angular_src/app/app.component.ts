import { Component, OnInit } from '@angular/core';
import { HelpersService } from './helpers/helpers.service';

@Component({
  selector: 'app-root',
  templateUrl: 'app.component.html',
  styles: []
})
export class AppComponent implements OnInit {
    // Is user logged in
    logged: Boolean = false;

    // Is current user admin
    is_admin: boolean = false;

    constructor(public helpersService: HelpersService) { }

    ngOnInit() {
        this.is_admin = this.helpersService.isAdmin();
    }

    /**
     * Handle events from child auth component
     * @param  {string} ev Event name
     */
    onSignInEvent(ev: string) {
        if (ev = 'logged') {
            // Switch from auth form to content
            this.logged = true;
        }
    }
}
