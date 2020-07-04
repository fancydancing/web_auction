import { Component, OnInit, Input, EventEmitter,  Output } from '@angular/core';
import { AucItem, ServerResponse } from '../item';
import { Bid } from '../bid';
import { RpcService } from '../rpc/rpc.service';
import { HelpersService } from '../helpers/helpers.service';

import { FormControl, Validators } from '@angular/forms';
import { FormGroup, FormBuilder } from '@angular/forms';

@Component({
  selector: 'item-card',
  templateUrl: './item-card.component.html',
  styles: []
})
export class ItemCardComponent implements OnInit {
    // Auction item id
    @Input() item_id: number;

    // Auction item
    @Input() item: AucItem;

    // False - view item
    // True - add new item or edit current item
    @Input() edit_mode: boolean;

    // Send events for parent list for closing card and updating list
    @Output() itemCardEvent: EventEmitter<string> = new EventEmitter<string>();

    // List of bids
    bids: Bid[] = [];

    // Field for submit new bid
    bid_price: number;

    // Item close datetime
    close_dt: Date;

    // Show countdown component
    countdown_init: boolean = false;

    // Left time in sec
    left_time: number;

    // Left time days
    time_left_days: number;

    // Columns of bids table
    bidsDisplayedColumns: string[] = ['user_name', 'price', 'date']; //

    // Validators for title
    titleFormControl = new FormControl('', [
        Validators.required
    ]);

    // Validators for price
    priceFormControl = new FormControl('', [
        Validators.required,
        Validators.max(100000)
    ]);

    // Validators for new bid
    bidFormControl = new FormControl('', [
        Validators.required,
        Validators.max(100000)
    ]);

    // Form for editing item
    form: FormGroup;

    // Form for submiting new bid
    formBid: FormGroup;

    constructor(
        private rpcService: RpcService,
        public helpersService: HelpersService,
        private formBuilder: FormBuilder
    ) { }

    ngOnInit() {
        this.updateCard();

        // Forms config. Validators setup
        this.form = this.formBuilder.group({
            titleInput: [null, Validators.required],
            descriptionInput: [null, Validators.required],
            priceInput: [Validators.required, Validators.max(100000)],
            closedtInput: [null, Validators.required]
        });

        this.formBid = this.formBuilder.group({
            bidInput: [Validators.required, Validators.max(100000)],
        });

    }

    /**
     * Get data from backend and fill fields for item and bids list
     */
    updateCard() {
        if (!this.item_id) {
            return;
        }

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
        this.item = item;
        this.bid_price = null;

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
            alert('You have to choose a time for closing the lot.');
            return;
        }
        this.item.close_dt = this.helpersService.getEpochFromDatetime(this.close_dt);
        this.rpcService.addItem(this.item)
            .subscribe(
                () => this.itemCardEvent.emit('new_item_created')
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
                () => this.itemCardEvent.emit('item_updated')
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

    /**
     * Filter for date picker. It allows to choose only datetime in future
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
        this.itemCardEvent.emit('item_card_closed');
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
            alert('You have to make a higher bid.');
            return;
        }

        if (this.bids.length > 0 && this.bids[0].user_name == this.helpersService.getUserName()) {
            alert('Your bid is already the highest.');
            return;
        }

        this.rpcService.makeBid(this.item_id, this.bid_price)
            .subscribe(res => this.makeBidHandler(res));
    }

    /**
     * Handle submit bid result. Updating card after every attempt
     * @param res Result of submiting bid
     */
    makeBidHandler(res: ServerResponse) {
        if (!res.result) {
            alert(res.msg);
        }

        this.updateCard();
    }
}
