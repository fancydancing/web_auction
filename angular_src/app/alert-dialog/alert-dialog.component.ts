import { Component, OnInit, EventEmitter, Output, Input } from '@angular/core';

@Component({
  selector: 'alert-dialog',
  templateUrl: './alert-dialog.component.html',
  styles: []
})
export class AlertDialogComponent implements OnInit {
    @Input() state;

    @Output() alertDialogEvent: EventEmitter<string> = new EventEmitter<string>();

    constructor() { }

    ngOnInit() {

    }

    close() {
        this.alertDialogEvent.emit('hide_dialog');
    }
}

export class AlertDialogState {
    public state = {
        showState: false, // show or hide dialog
        msg: '', // msg to show
        msg_queue: []
    }

    /**
     * Handler for events from dialog
     * @param ev Event from dialog
     */
    public onAlertDialogEvent(ev) {
        if (ev == 'hide_dialog') {
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
