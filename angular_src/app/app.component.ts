import { Component, OnInit } from '@angular/core';
import { HelpersService } from './helpers/helpers.service';
import { CommunicationService } from './communication/communication.service';
import { AlertDialogState } from './alert-dialog/alert-dialog.component';
import { ServerMsg } from './item';


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

    // Websocket
    webSocketChannel: WebSocket;

    // Initial Sign In form for user
    viewName = 'sign-in'

    // Alert dialog state
    alertDialog: AlertDialogState = new AlertDialogState();


    constructor(
        public helpersService: HelpersService,
        public communicationService: CommunicationService
    ) { }

    ngOnInit() {
        this.is_admin = this.helpersService.isAdmin();

        // Connect and subscribe to websocket
        let ws_url = 'wss://' + window.location.host + '/ws/channel/';
        this.webSocketChannel = new WebSocket(ws_url);
        this.webSocketChannel.onmessage = (e => this.onWebSocketMsg(e));

        this.communicationService.serverMsgAnnounced$.subscribe(
            msg => this.messageHandler(msg)
        );
    }

    /**
     * Broadcast message from websocket through communicationService
     * @param  {} e Websocket message
     */
    onWebSocketMsg(e) {
        let data = JSON.parse(e.data);
        this.communicationService.announceServerMsg(data.message);
    }

    /**
     *Handler for websocket messages
     * @param  {ServerMsg} msg Websocket message
     */
    messageHandler(msg: ServerMsg) {
        let user_id = this.helpersService.getUserId();

        if (msg.event == 'item_won' && msg.user_id == user_id) {
            this.alertDialog.open('You won: "' + msg.item_title + '"');
            return;
        }

        if (msg.event == 'autobid_exceeding' && msg.user_id == user_id) {
            let alert_msg = (
                'The autobiding threshold is exceeded ' +
                '$' + msg.autobid_spent.toString() + '/' +
                '$' + msg.autobid_total_sum.toString()
            );
            this.alertDialog.open(alert_msg);
            return;
        }

        if (msg.event == 'item_losing' && msg.user_id == user_id) {
            let alert_msg = (
                'Your bid ' +
                '$' + msg.user_bid_price.toString() +
                ' on item ' +
                '"' + msg.item_title + '"' +
                ' was outbided (' +
                '$' + msg.item_price.toString() + ')'
            );
            this.alertDialog.open(alert_msg);
            return;
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
                this.viewName = 'items-list';
            } else {
                this.viewName = 'gallery';
            }
        }
    }

    /**
     * Switch to User Page
     */
    onUserProfile() {
        this.viewName = 'user-page';
        this.communicationService.announceRootMsg('close_card');
    }

    /**
     * Switch to Admin Panel
     */
    onAdminPanel() {
        if (this.is_admin) {
            this.viewName = 'items-list';
            this.communicationService.announceRootMsg('close_card');
        } else {
            this.alertDialog.open('You are not admin.');
        }
    }

    /**
     * Switch to Gallery page
     */
    onGallery() {
        this.viewName = 'gallery';
        this.communicationService.announceRootMsg('close_card');
    }
}
