import { Component, OnInit, Input, EventEmitter,  Output } from '@angular/core';
import { AucItem, Bid, ServerResponse, ItemCardEvent, AucUserItem, MainView } from '../item';
import { AlertDialogState } from '../alert-dialog/alert-dialog.component';
import { RpcService } from '../rpc/rpc.service';
import { HelpersService } from '../helpers/helpers.service';
import { CommunicationService } from '../communication/communication.service';

import { FormControl, Validators } from '@angular/forms';
import { FormGroup, FormBuilder } from '@angular/forms';

@Component({
  selector: 'user-page',
  templateUrl: './user-page.component.html',
  styles: []
})
export class UserPageComponent implements OnInit {
    mode: String = MainView.List;

    // Pass enum MainView to template
    mainView = MainView;

    selectedItemId: number = null;

    won_items: AucUserItem[];

    items: AucUserItem[];

    wonDisplayedColumns: string[] = ['item', 'user_price', 'close_dt'];

    lastDisplayedColumns: string[] = ['status', 'item', 'user_price', 'close_dt'];

    constructor(
        private rpcService: RpcService,
        public helpersService: HelpersService,
        public communicationService: CommunicationService,
        private formBuilder: FormBuilder
    ) { }

    ngOnInit() {
        this.updateUserPage();
    }

    updateUserPage() {
        this.rpcService.getUserItems({'status': 'won'})
            .subscribe(items => this.won_items = items);

        this.rpcService.getUserItems({})
            .subscribe(items => this.items = items);
    }

    getUserName() {
        return this.helpersService.getUserName();
    }

    getColorByStatus(status) {
        if (status == 'won') {
            return 'green';
        } else if (status == 'lost') {
            return 'red';
        } else if (status == 'in_progress') {
            return 'blue';
        }
    }

    getColorForPrice(item: AucUserItem) {
        if (item.close_dt < this.helpersService.getCurrentEpoch()) {
            return 'black';
        }

        if (item.user_price < item.max_price) {
            return 'red'
        } else {
            return 'green'
        }
    }

    getTextByStatus(status) {
        if (status == 'won') {
            return 'Won';
        } else if (status == 'lost') {
            return 'Lost';
        } else if (status == 'in_progress') {
            return 'In progress';
        }
    }

    onSelect(item_id) {
        this.selectedItemId = item_id;
        this.mode = MainView.Item;
    }

    getListViewDisplay() {
        if (this.mode == MainView.List) {
            return 'block';
        }
        return 'none';
    }

    onItemCardEvent(ev: ItemCardEvent) {
        if (ev == ItemCardEvent.NewItemCreated) {
            this.setListViewMode(true);
        } else {
            this.setListViewMode(true);
        }
    }

    setListViewMode(refresh_list: Boolean): void {
        this.mode = MainView.List;
        if (refresh_list) {
            this.updateUserPage();
        }
    }
}
