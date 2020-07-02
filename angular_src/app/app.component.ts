import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: 'app.component.html',
  styles: []
})
export class AppComponent implements OnInit {
    logged: Boolean = false;

    constructor() { }

    ngOnInit() {
    }

    onSignInEvent(ev: String) {
        if (ev = 'logged') {
            this.logged = true;
        }
    }
}
