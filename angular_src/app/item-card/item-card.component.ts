import { Component, OnInit, Input, EventEmitter,  Output } from '@angular/core';
import { AucItem } from '../item';
import { Bid } from '../bid';
import { RpcService } from '../rpc/rpc.service';
import { HelpersService } from '../helpers/helpers.service';

import { FormControl, Validators } from '@angular/forms';
import { FormGroup, FormBuilder } from '@angular/forms';
import { ErrorStateMatcher } from '@angular/material/core';


export class MyErrorStateMatcher implements ErrorStateMatcher {
    isErrorState(control, form): boolean {
        const isSubmitted = form && form.submitted;
        return !!(control && control.invalid && (control.dirty || control.touched || isSubmitted));
    }
}


@Component({
  selector: 'item-card',
  templateUrl: './item-card.component.html',
  styles: []
})
export class ItemCardComponent implements OnInit {
    @Input() item_id: Number;
    @Input() item: AucItem;
    @Input() edit_mode: Boolean;
    @Output() itemCardEvent: EventEmitter<string> = new EventEmitter<string>();
    bids: Bid[] = [];
    bid_price: Number;
    moment;

    countdown_init: boolean = false;
    left_time: number;

    displayedColumns: string[] = ['user_name', 'price', 'date'];

    titleFormControl = new FormControl('', [
        Validators.required
    ]);

    priceFormControl = new FormControl('', [
        Validators.required,
        Validators.max(100000)
    ]);

    bidFormControl = new FormControl('', [
        Validators.required,
        Validators.max(100000)
    ]);

    matcher = new MyErrorStateMatcher();

    form: FormGroup;
    formBid: FormGroup;

    constructor(
        private rpcService: RpcService,
        public helpersService: HelpersService,
        private formBuilder: FormBuilder
    ) { }

    ngOnInit() {
        this.getItem();

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

    getItem(): void {
        if (!this.item_id) {
            return;
        }

        this.updateCard();
    }

    updateCard() {
        this.rpcService.getItem(this.item_id)
            .subscribe(item => this.initItem(item));

        this.getBids();

        this.bid_price = null;
    }

    initItem(item) {
        this.item = item;
        let dt = new Date(0);
        dt.setUTCSeconds(item.close_dt);
        this.moment = dt;

        let epoch = Math.round(Date.now() / 1000);
        this.left_time = item.close_dt - epoch;
        this.left_time = this.left_time > 0 ? this.left_time : 0;
        this.countdown_init = true;
    }

    getBids(): void {
        this.rpcService.getBids(this.item_id)
            .subscribe(bids => this.bids = bids);
    }

    addItem(): void {
        if (!this.form.valid) {
            this.validateAllFormFields(this.form);
            return;
        }

        if (!this.moment) {
            alert('You have to choose a time for closing the lot.');
            return;
        }
        this.item.close_dt = Math.round(this.moment.getTime() / 1000);
        this.rpcService.addItem(this.item)
            .subscribe(
                () => this.itemCardEvent.emit('new_item_created')
            );
    }

    updateItem(): void {
        if (!this.form.valid) {
            this.validateAllFormFields(this.form);
            return;
        }

        this.item.close_dt = Math.round(this.moment.getTime() / 1000);
        this.rpcService.updateItem(this.item)
            .subscribe(
                () => this.itemCardEvent.emit('item_updated')
            );
    }

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

    myFilter(d: Date): boolean {
        let dateTime = new Date();
        return d > dateTime;
    }

    closeItemCard(): void {
        this.itemCardEvent.emit('item_card_closed');
    }

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

    makeBidHandler(res) {
        if (!res.result) {
            alert(res.msg);
        }
        this.updateCard();
    }
}
