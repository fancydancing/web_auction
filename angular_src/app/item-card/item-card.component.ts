import { Component, OnInit, Input, EventEmitter,  Output } from '@angular/core';
import { AucItem, Bid, ServerResponse, ItemCardEvent } from '../item';
import { AlertDialogState } from '../alert-dialog/alert-dialog.component';
import { RpcService } from '../rpc/rpc.service';
import { HelpersService } from '../helpers/helpers.service';
import { CommunicationService } from '../communication/communication.service';

import { FormControl, Validators } from '@angular/forms';
import { FormGroup, FormBuilder } from '@angular/forms';
import { reduce } from 'rxjs/operators';

@Component({
  selector: 'item-card',
  templateUrl: './item-card.component.html',
  styles: []
})
export class ItemCardComponent implements OnInit {
    // Auction item id
    @Input() item_id: number;

    // Auction item
    @Input() item: AucItem = {};

    // False - view item
    // True - add new item or edit current item
    @Input() edit_mode: boolean;

    // Send events for parent list for closing card and updating list
    @Output() itemCardEvent: EventEmitter<ItemCardEvent> = new EventEmitter<ItemCardEvent>();

    // Alert dialog state
    alertDialog: AlertDialogState = new AlertDialogState();

    // List of bids
    bids: Bid[] = [];

    // Field for submit new bid
    bid_price: number;

    auto_bid: boolean = false;

    // Item close datetime
    close_dt: Date;

    // Show countdown component
    countdown_init: boolean = false;

    // Left time in sec
    left_time: number;

    // Left time days
    time_left_days: number;

    // Columns of bids table
    bidsDisplayedColumns: string[] = ['user_name', 'price', 'date'];

    // Validators for title
    titleFormControl = new FormControl('', [
        Validators.required
    ]);

    // Validators for price
    priceFormControl = new FormControl('', [
        Validators.required,
        Validators.min(0),
        Validators.max(100000)
    ]);

    // Validators for new bid
    bidFormControl = new FormControl('', [
        Validators.required,
        Validators.min(0),
        Validators.max(100000)
    ]);

    // Form for editing item
    form: FormGroup;

    // Form for submitting new bid
    formBid: FormGroup;

    constructor(
        private rpcService: RpcService,
        public helpersService: HelpersService,
        public communicationService: CommunicationService,
        private formBuilder: FormBuilder
    ) { }

    ngOnInit() {
        this.updateCard();

        // Forms config. Validators setup
        this.form = this.formBuilder.group({
            titleInput: [null, Validators.compose([Validators.required])],
            descriptionInput: [null, Validators.compose([Validators.required])],
            priceInput: [
                null,
                Validators.compose([
                    Validators.required,
                    Validators.min(0),
                    Validators.max(100000)
                ])
            ],
            closedtInput: [null, Validators.compose([Validators.required])]
        });

        this.formBid = this.formBuilder.group({
            bidInput: [null, Validators.compose([
                Validators.required,
                Validators.min(0),
                Validators.max(100000)
            ])],
        });

        this.communicationService.serverMsgAnnounced$.subscribe(
            msg => this.messageHandler(msg)
        );
    }

    messageHandler(msg) {
        // this.alertDialog.open(msg.item_id.toString())
        if (msg.event == 'new_bid' && msg.item_id == this.item_id) {
            this.updateCard();
            return
        }

        if (msg.event == 'item_changed' && msg.item_id == this.item_id) {
            this.updateCard();
            return
        }
    }

    /**
     * Get data from backend and fill fields for item and bids list
     */
    updateCard() {
        if (!this.item_id) {
            return;
        }

        //this.item = {};

        this.rpcService.getItem(this.item_id)
            .subscribe(item => this.getItemHandler(item));

        this.rpcService.getBids(this.item_id)
            .subscribe(bids => this.bids = bids);
    }

    /**
     * Init calculated fields of item's card
     * @param  {AucItem} item Auction item from backend
     */
    getItemHandler(item: AucItem) {
        if (!item || !item.id) {
            this.item = {};
            this.itemCardEvent.emit(ItemCardEvent.ItemNotFound);
            return;
        }

        this.item = item;

        //this.bid_price = null;
        // this.formBid.reset();
        // Object.keys(this.formBid.controls).forEach(key => {
        //     this.formBid.controls[key].reset();
        //     this.formBid.controls[key].setErrors(null);
        // });
        // this.markAllAsUntouched(this.formBid);


        this.close_dt = this.helpersService.getDateFromEpoch(item.close_dt);
        let epoch = this.helpersService.getCurrentEpoch();

        this.left_time = item.close_dt - epoch;
        this.left_time = this.left_time > 0 ? this.left_time : 0;
        this.time_left_days = Math.floor(this.left_time / 86400); // 86400 secs in day
        this.countdown_init = true;
    }

    /**
     * Adding new item
     */
    addItem(): void {
        if (!this.form.valid) {
            this.validateAllFormFields(this.form);
            return;
        }

        if (!this.close_dt) {
            this.alertDialog.open('You have to choose a time for closing the lot.');
            return;
        }
        this.item.close_dt = this.helpersService.getEpochFromDatetime(this.close_dt);
        this.rpcService.addItem(this.item)
            .subscribe(
                () => this.itemCardEvent.emit(ItemCardEvent.NewItemCreated)
            );
    }

    /**
     * Validate form and update item in DB
     */
    updateItem(): void {
        if (!this.form.valid) {
            this.validateAllFormFields(this.form);
            return;
        }

        this.item.close_dt = this.helpersService.getEpochFromDatetime(this.close_dt);
        this.rpcService.updateItem(this.item)
            .subscribe(
                () => this.itemCardEvent.emit(ItemCardEvent.ItemUpdated)
            );
    }

    /**
     * Validate whole form
     * @param formGroup form group for validation
     */
    validateAllFormFields(formGroup: FormGroup) {
        Object.keys(formGroup.controls).forEach(field => {
            const control = formGroup.get(field);
            if (control instanceof FormControl) {
                control.markAsTouched({ onlySelf: true });
            } else if (control instanceof FormGroup) {
                this.validateAllFormFields(control);
            }
        });
    }

    markAllAsUntouched(formGroup: FormGroup) {
        Object.keys(formGroup.controls).forEach(field => {
            const control = formGroup.get(field);
            if (control instanceof FormControl) {
                control.markAsUntouched({ onlySelf: true });
            }
        });
    }

    /**
     * Filter for date picker. It allows to choose datetime only in future
     * @param d Date for datetime picker
     */
    myFilter(d: Date): boolean {
        let dateTime = new Date();
        return d > dateTime;
    }

    /**
     * Close card and back to listview
     */
    closeItemCard(): void {
        this.itemCardEvent.emit(ItemCardEvent.ItemCardClosed);
    }

    /**
     * Send new bid for item
     */
    makeBid(): void {
        if (!this.formBid.valid) {
            this.validateAllFormFields(this.form);
            return;
        }

        if (!this.bid_price) {
            this.bid_price = 0;
        }

        if (this.bids.length > 0 && this.bids[0].price >= this.bid_price) {
            this.alertDialog.open('You have to make a higher bid.');
            return;
        }

        if (this.bids.length > 0 && this.bids[0].user_name == this.helpersService.getUserName()) {
            this.alertDialog.open('Your bid is already the highest.');
            return;
        }

        this.rpcService.makeBid(this.item_id, this.bid_price)
            .subscribe(res => this.makeBidHandler(res));

        this.bid_price = 0;
    }

    /**
     * Handle submit bid result. Updating card after every attempt
     * @param res Result of submitting bid
     */
    makeBidHandler(res: ServerResponse) {
        if (!res.result) {
            this.alertDialog.open(res.msg);
        }

        this.updateCard();
    }

    autoBidChange() {
        let user_id = this.helpersService.getUserId();
        this.rpcService.autoBid(this.item_id, user_id, this.auto_bid)
            .subscribe(res => this.autoBidHandler(res));
    }

    autoBidHandler(res) {
        if (res.result) {
            if (res.auto_bid_state) {
                this.alertDialog.open('Auto bid enabled')
            } else {
                this.alertDialog.open('Auto bid disabled')
            }
        } else {
            this.alertDialog.open('You should set total auto bid sum first.')
            this.auto_bid = res.auto_bid_state
        }
    }
}
