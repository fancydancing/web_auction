import { Component, OnInit, Input, EventEmitter,  Output } from '@angular/core';
import { AucItem, Bid, ServerResponse, ItemCardEvent, AucUserItem, MainView, UserInfo } from '../item';
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
    userInfo: UserInfo = {};
    mode: String = MainView.List;

    // Pass enum MainView to template
    mainView = MainView;

    selectedItemId: number = null;

    won_items: AucUserItem[];

    items: AucUserItem[];

    wonDisplayedColumns: string[] = ['item', 'user_price', 'close_dt'];

    lastDisplayedColumns: string[] = ['status', 'item', 'user_price', 'dt'];

    // Form for editing user profile
    formGroup: FormGroup;
    emailFormControl = new FormControl('', [Validators.email]);

    constructor(
        private rpcService: RpcService,
        public helpersService: HelpersService,
        public communicationService: CommunicationService,
        private formBuilder: FormBuilder
    ) { }

    ngOnInit() {
        // Forms config. Validators setup
        this.formGroup = this.formBuilder.group({
            emailControl: [
                null,
                Validators.compose([
                    Validators.email
                ])
            ],

            autobidTotalSum: [
                null,
                Validators.compose([
                    Validators.min(0),
                    Validators.max(100000)
                ])
            ],
            autobidAlertPerc: [
                null,
                Validators.compose([
                    Validators.min(0),
                    Validators.max(100)
                ])
            ],
        });

        this.updateUserPage();

        this.communicationService.rootMsgAnnounced$.subscribe(
            msg => this.rootMessageHandler(msg)
        );
    }

    rootMessageHandler(msg) {
        if (msg == 'close_card') {
            this.setListViewMode(false);
        }
    }

    getErrorMessage() {
          return this.emailFormControl.hasError('email') ? 'Not a valid email' : '';
    }

    updateUserPage() {
        this.rpcService.getUser(this.helpersService.getUserId())
            .subscribe(userInfo => this.userInfo = userInfo);

        this.rpcService.getUserItems({'status': 'won', 'sort': 'close_dt'})
            .subscribe(items => this.won_items = items);

        this.rpcService.getUserItems({'sort': 'bid_dt'})
            .subscribe(items => this.items = items);
    }

    updateUserInfo() {
        if (!this.formGroup.valid) {
            this.helpersService.validateAllFormFields(this.formGroup);
            return;
        }

        this.rpcService.updateUserInfo(this.userInfo)
            .subscribe(
                () => {}
            );
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
            return 'red';
        } else {
            return 'green';
        }
    }

    getTooltipForPrice(item: AucUserItem) {
        if (item.close_dt < this.helpersService.getCurrentEpoch()) {
            return 'Auction for item is closed';
        }

        if (item.user_price < item.max_price) {
            return 'You have been outbidded';
        } else {
            return 'Your bid is highest';
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
