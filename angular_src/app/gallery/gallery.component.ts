import { Component, OnInit } from '@angular/core';
import { AucItem } from '../item';
import { RpcService } from '../rpc/rpc.service';
import { HelpersService } from '../helpers/helpers.service';


@Component({
  selector: 'gallery',
  templateUrl: 'gallery.component.html',
  styles: []
})
export class GalleryComponent implements OnInit {
    items: AucItem[];
    selectedItem: AucItem;
    mode: String = 'list_view';

    constructor(
        private rpcService: RpcService,
        public helpersService: HelpersService,
    ) { }

    ngOnInit() {
        this.getItems();
    }

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

    handleResult(data) {
        this.items = data.items;
    }

    onSelect(item: AucItem): void {
        this.selectedItem = item;
        this.mode = 'item_view';
    }

    setListViewMode(refresh_list: Boolean): void {
        this.mode = 'list_view';
        if (refresh_list) {
            this.getItems();
        }
    }

    onItemCardEvent(ev: String) {
        if (ev == 'new_item_created') {
            this.setListViewMode(true);
        } else if (ev == 'item_card_closed') {
            this.setListViewMode(false);
        } else if (ev == 'item_updated') {
            this.setListViewMode(true);
        }
    }

    getListViewDisplay() {
        if (this.mode == 'list_view') {
            return 'block';
        }
        return 'none';
    }
}

