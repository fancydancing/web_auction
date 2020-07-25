import { Component, OnInit } from '@angular/core';
import { HelpersService } from './helpers/helpers.service';
import { CommunicationService } from './communication/communication.service';
import { AlertDialogState } from './alert-dialog/alert-dialog.component';


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

    viewName = 'sign-in'

    // Alert dialog state
    alertDialog: AlertDialogState = new AlertDialogState();


    constructor(
        public helpersService: HelpersService,
        public communicationService: CommunicationService
    ) { }

    ngOnInit() {
        this.is_admin = this.helpersService.isAdmin();

        let ws_url = 'ws://' + window.location.host + '/ws/channel/';
        const chatSocket = new WebSocket(ws_url);

        chatSocket.onmessage = (e => this.onWebSocketMsg(e));

        this.communicationService.serverMsgAnnounced$.subscribe(
            msg => this.messageHandler(msg)
        );

    }

    onWebSocketMsg(e) {
        let data = JSON.parse(e.data);
        this.communicationService.announceServerMsg(data.message);
    }

    messageHandler(msg) {
        if (msg.user_id == this.helpersService.getUserId() && msg.event == 'item_won') {
            this.alertDialog.open('You won: "' + msg.item_title + '"');
        }
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

            if (this.is_admin) {
                this.viewName = 'items-list'
            } else {
                this.viewName = 'gallery'
            }
        }
    }

    onUserProfile() {
        this.viewName = 'user-page'
    }

    onAdminPanel() {
        if (this.is_admin) {
            this.viewName = 'items-list'
        } else {
            this.alertDialog.open('You are not admin.');
        }
    }

    onGallery() {
        this.viewName = 'gallery'
    }
}
