import { Component, OnInit, Input, EventEmitter,  Output } from '@angular/core';
import { AucItem } from '../item';
import { Bid } from '../bid';
import { RpcService } from '../rpc/rpc.service';
import { HelpersService } from '../helpers/helpers.service';


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
    moment_new;

    displayedColumns: string[] = ['user_name', 'price', 'bid_dt'];


    constructor(private rpcService: RpcService, public helpersService: HelpersService) { }

    ngOnInit() {
        this.getItem();
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
    }

    initItem(item) {
        this.item = item;
        let dt = new Date(0);
        dt.setUTCSeconds(item.close_dt);
        this.moment = dt;

    }

    getBids(): void {
        this.rpcService.getBids(this.item_id)
            .subscribe(bids => this.bids = bids);
    }

    addItem(): void {
        if (!this.moment_new) {
            alert('You have to choose a time for closing the lot.');
            return;
        }
        this.item.close_dt = Math.round(this.moment_new.getTime() / 1000);
        this.rpcService.addItem(this.item)
            .subscribe(
                () => this.itemCardEvent.emit('new_item_created')
            );
    }

    updateItem(): void {
        this.item.close_dt = Math.round(this.moment.getTime() / 1000);
        this.rpcService.updateItem(this.item)
            .subscribe(
                () => this.itemCardEvent.emit('item_updated')
            );
    }

    closeItemCard(): void {
        this.itemCardEvent.emit('item_card_closed');
    }

    makeBid(): void {
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
            .subscribe(() => this.updateCard());
    }
}
