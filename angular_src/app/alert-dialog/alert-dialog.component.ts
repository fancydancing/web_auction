import { Component, OnInit, EventEmitter, Output, Input } from '@angular/core';

@Component({
  selector: 'alert-dialog',
  templateUrl: './alert-dialog.component.html',
  styles: []
})
export class AlertDialogComponent implements OnInit {
    // Dialog state
    @Input() state: AlertState;

    // Channel for sending closing event to parent component
    @Output() alertDialogEvent: EventEmitter<AlertEvent> = new EventEmitter<AlertEvent>();

    constructor() { }

    ngOnInit() {

    }

    /**
     * Close alert dialog
     */
    close() {
        this.alertDialogEvent.emit(AlertEvent.HideDialog);
    }
}

export class AlertDialogState {
    public state: AlertState = {
        showState: false,
        msg: '',
        msg_queue: []
    }

    /**
     * Handler for events from dialog
     * @param ev Event from dialog
     */
    public onAlertDialogEvent(ev: AlertEvent) {
        if (ev == AlertEvent.HideDialog) {
            this.showNext();
        }
    }

    /**
     * Open dialog with message
     * @param msg Message to display
     */
    public open(msg: string) {
        this.state.msg_queue.push(msg);
        if (!this.state.showState) {
            this.showNext();
        }
    }

    /**
     * Show next dialog in queue
     */
    public showNext() {
        let m = this.state.msg_queue.shift();
        if (m) {
            this.state.msg = m;
            this.state.showState = true;
        } else {
            this.state.showState = false;
        }
    }
}

export enum AlertEvent {
    // Events for alert dialog

    HideDialog = 'hide_dialog',
}


export interface AlertState {
    // Alert dialog state

    showState: boolean; // show or hide dialog

    msg: string; // current msg to show

    msg_queue: Array<string>; // queue of messages
}

