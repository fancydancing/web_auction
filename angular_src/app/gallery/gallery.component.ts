import { Component, OnInit } from '@angular/core';
import { AucItem, AucItems, MainView, ItemCardEvent } from '../item';
import { RpcService } from '../rpc/rpc.service';
import { HelpersService } from '../helpers/helpers.service';
import { CommunicationService } from '../communication/communication.service';


@Component({
  selector: 'gallery',
  templateUrl: 'gallery.component.html',
  styles: []
})
export class GalleryComponent implements OnInit {
    // List of items
    items: AucItem[];

    // Selected item
    selectedItem: AucItem;

    // Mode of content
    mode: String = MainView.List;

    // Pass enum MainView to template
    mainView = MainView;

    constructor(
        private rpcService: RpcService,
        public helpersService: HelpersService,
        public communicationService: CommunicationService
    ) { }

    ngOnInit() {
        this.getItems();

        // Subscribe to frontend messages
        this.communicationService.rootMsgAnnounced$.subscribe(
            msg => this.rootMessageHandler(msg)
        );
    }

    /**
     * @param  {string} msg incoming message
     */
    rootMessageHandler(msg: string) {
        if (msg == 'close_card') {
            this.setListViewMode(false);
        }
    }

    /**
     * Request items list from backend
     */
    getItems(): void {
        this.rpcService.getItems({
            page: 0,
            page_size: -1,
            sort: 'create_dt',
            order: 'desc',
            show_closed: false
        })
        .subscribe(data => this.handleResult(data));
    }

    /**
     * Handler of items list request
     * @param data
     */
    handleResult(data: AucItems) {
        this.items = data.items;
    }

    /**
     * Select item handler
     * @param item Selected item
     */
    onSelect(item: AucItem): void {
        this.selectedItem = item;
        this.mode = MainView.Item;
    }

    /**
     * Switch to list view (from card view) and refresh it if needed
     * @param refresh_list Refresh items list or not
     */
    setListViewMode(refresh_list: Boolean): void {
        this.mode = MainView.List;
        if (refresh_list) {
            this.getItems();
        }
    }

    /**
     * Handler of child item card events
     * @param ev Event from child item card
     */
    onItemCardEvent(ev: ItemCardEvent) {
        if (ev == ItemCardEvent.NewItemCreated) {
            this.setListViewMode(true);
        } else if (ev == ItemCardEvent.ItemCardClosed) {
            this.setListViewMode(true);
        } else if (ev == ItemCardEvent.ItemUpdated) {
            this.setListViewMode(true);
        }
    }

    /**
     * Get style for list view 'display' option
     *   'block' - Show list view
     *   'none' - Show item card
     */
    getListViewDisplay() {
        if (this.mode == MainView.List) {
            return 'block';
        }
        return 'none';
    }
}

