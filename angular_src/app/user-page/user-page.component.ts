import { Component, OnInit } from '@angular/core';
import { ItemCardEvent, AucUserItem, MainView, UserInfo, BidStatus } from '../item';
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

    // Mode of content
    mode: String = MainView.List;

    // Pass enum MainView to template
    mainView = MainView;

    // Select Item ID
    selectedItemId: number = null;

    // List of awarded items
    won_items: AucUserItem[];

    // List of recent bids
    items: AucUserItem[];

    // Columns of awarded items table
    wonDisplayedColumns: string[] = ['item', 'user_price', 'close_dt'];

    // Columns of recent bids table
    lastDisplayedColumns: string[] = ['status', 'item', 'user_price', 'dt'];

    // Form for editing user profile
    formGroup: FormGroup;

    // Email field form control
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

    /**
     * @param  {string} msg incoming message
     */
    rootMessageHandler(msg: string): void {
        if (msg == 'close_card') {
            this.setListViewMode(false);
        }
    }

    /**
     * Get email field error message
     */
    getErrorMessage(): string {
          return this.emailFormControl.hasError('email') ? 'Not a valid email' : '';
    }

    /**
     * Reload data for user page
     */
    updateUserPage(): void {
        this.rpcService.getUser(this.helpersService.getUserId())
            .subscribe(userInfo => this.userInfo = userInfo);

        this.rpcService.getUserItems({'status': 'won', 'sort': 'close_dt'})
            .subscribe(items => this.won_items = items);

        this.rpcService.getUserItems({'sort': 'bid_dt'})
            .subscribe(items => this.items = items);
    }

    /**
     * Update user info
     */
    updateUserInfo(): void {
        if (!this.formGroup.valid) {
            this.helpersService.validateAllFormFields(this.formGroup);
            return;
        }

        this.rpcService.updateUserInfo(this.userInfo)
            .subscribe(
                () => {}
            );
    }

    /**
     * Get color for bid
     * @param  {} status Status of bid
     */
    getColorByStatus(status: string): string {
        if (status == BidStatus.Won) {
            return 'green';
        } else if (status == BidStatus.Lost) {
            return 'red';
        } else if (status == BidStatus.InProgress) {
            return 'blue';
        }
    }

    /**
     * Get color for user bid price
     * @param  {AucUserItem} item Auction item
     */
    getColorForPrice(item: AucUserItem): string {
        if (item.close_dt < this.helpersService.getCurrentEpoch()) {
            return 'black';
        }

        if (item.user_price < item.max_price) {
            return 'red';
        } else {
            return 'green';
        }
    }

    /**
     * Get text for tooltip for users bid price
     * @param  {AucUserItem} item Auction item
     */
    getTooltipForPrice(item: AucUserItem): string {
        if (item.close_dt < this.helpersService.getCurrentEpoch()) {
            return 'Auction for item is closed';
        }

        if (item.user_price < item.max_price) {
            return 'You have been outbidded';
        } else {
            return 'Your bid is highest';
        }
    }

    /**
     * Get text status for user bid
     * @param  {string} status Status of users bid
     */
    getTextByStatus(status: string): string {
        if (status == BidStatus.Won) {
            return 'Won';
        } else if (status == BidStatus.Lost) {
            return 'Lost';
        } else if (status == BidStatus.InProgress) {
            return 'In progress';
        }
    }

    /**
     * Handler for item select in user page
     * @param  {number} item_id
     */
    onSelect(item_id: number): void {
        this.selectedItemId = item_id;
        this.mode = MainView.Item;
    }

    /**
     * Get style for list view 'display' option
     *   'block' - Show list view
     *   'none' - Show item card
     */
    getListViewDisplay(): string {
        if (this.mode == MainView.List) {
            return 'block';
        }
        return 'none';
    }

    /**
     * Handler of child item card events
     * @param ev Event from child item card
     */
    onItemCardEvent(ev: ItemCardEvent): void {
        if (ev == ItemCardEvent.NewItemCreated) {
            this.setListViewMode(true);
        } else {
            this.setListViewMode(true);
        }
    }

    /**
     * Switch to list view (from card view) and refresh it if needed
     * @param refresh_list Refresh items list or not
     */
    setListViewMode(refresh_list: Boolean): void {
        this.mode = MainView.List;
        if (refresh_list) {
            this.updateUserPage();
        }
    }
}
