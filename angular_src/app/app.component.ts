import { Component, OnInit } from '@angular/core';
import { HelpersService } from './helpers/helpers.service';
import { CommunicationService } from './communication/communication.service';


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

    chatSocket: WebSocket;

    constructor(
        public helpersService: HelpersService,
        public communicationService: CommunicationService
    ) { }

    ngOnInit() {
        this.is_admin = this.helpersService.isAdmin();

        const chatSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/channel/'
        );

        chatSocket.onmessage = (e => this.onWebSocketMsg(e));
    }

    onWebSocketMsg(e) {
        let data = JSON.parse(e.data);
        this.communicationService.announceServerMsg(data.message);
        console.log(data.message);
    }

    /**
     * Handle events from child auth component
     * @param  {string} ev Event name
     */
    onSignInEvent(ev: string) {
        if (ev = 'logged') {
            this.is_admin = this.helpersService.isAdmin();

            // Switch from auth form to content
            this.logged = true;
        }
    }
}
