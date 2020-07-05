import { Component, ViewEncapsulation, ViewChild, AfterViewInit } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';

import { Subject, merge } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { map, startWith, switchMap, delay } from 'rxjs/operators';

import { AucItem, AucItems, MainView, ItemCardEvent } from '../item';
import { RpcService } from '../rpc/rpc.service';
import { HelpersService } from '../helpers/helpers.service';
import { AlertDialogState } from '../alert-dialog/alert-dialog.component';


@Component({
  selector: 'items-list',
  templateUrl: './items-list.component.html',
  styles: [],
  encapsulation: ViewEncapsulation.None
})
export class ItemsListComponent implements AfterViewInit  {
    // List of items
    items: AucItem[];

    // Selected item
    selectedItem: AucItem;

    // Show list view at the beginning
    mode: MainView = MainView.List;

    // Filter by name and description
    search_string: String = null;

    // Observable stream of search string
    searchTerms: Subject<string> = new Subject<string>();

    // Is current user admin
    is_admin: boolean = false;

    // Columns of items table
    itemsDisplayedColumns: string[] = ['title', 'price', 'create_dt'];

    // Total items in DB
    resultsLength = 0;

    // Pass enum MainView to template
    mainView = MainView;

    // Alert dialog state
    alertDialog: AlertDialogState = new AlertDialogState();
    
    // Items table paginator
    @ViewChild(MatPaginator) paginator: MatPaginator;

    // Items table sorting columns headers
    @ViewChild(MatSort) sort: MatSort;

    constructor(
        private rpcService: RpcService,
        public helpersService: HelpersService
    ) {
        this.is_admin = this.helpersService.isAdmin();

        if (this.is_admin) {
            // Only admin have 'delete', 'edit' buttons
            this.itemsDisplayedColumns.push('operations');
        }
    }

    ngAfterViewInit() {
         // If the user changes the sort order, reset back to the first page.
        this.sort.sortChange.subscribe(() => this.paginator.pageIndex = 0);

        // Request data from backend if sorting or paging changed
        merge(this.sort.sortChange, this.paginator.page)
            .pipe(
                startWith({}),
                delay(0),
                switchMap(() => {
                    return this.rpcService.getItems({
                        page: this.paginator.pageIndex,
                        sort: this.sort.active,
                        order: this.sort.direction,
                        search_string: this.search_string,
                        show_closed: true
                    });
                }),
                map(data => {
                    this.resultsLength = data.total_count;
                    return data.items;
                }),
            ).subscribe(items => this.items = items);

        this.searchTerms.pipe(
            // wait 1000ms after each keystroke before considering the term
            debounceTime(1000),

            // ignore new term if same as previous term
            distinctUntilChanged()

        ).subscribe((term: string) => this.startSearch(term));
    }

    /**
     * Start search request to backend
     * @param term value of search string
     */
    startSearch(term: string): void {
        this.search_string = term;
        this.getItems();
    }

    /**
     * Push a search term into the observable stream.
     * @param term value of search string
     */
    search(term: string): void {
        this.searchTerms.next(term);
    }

    /**
     * Request items list from server
     */
    getItems(): void {
        this.rpcService.getItems({
            page: this.paginator.pageIndex,
            sort: this.sort.active,
            order: this.sort.direction,
            search_string: this.search_string,
            show_closed: true
        })
        .subscribe(data => this.handleResult(data));
    }

    /**
     * Handle get items request answer
     * @param data result from server
     */
    handleResult(data: AucItems) {
        this.resultsLength = data.total_count;
        this.items = data.items;
    }

    /**
     * Select item handler
     * @param item selected item
     */
    onSelect(item: AucItem): void {
        this.selectedItem = item;
        this.mode = MainView.Item;
    }

    /**
     * Edit item handler
     * @param item selected item
     */
    onSelectEdit(item: AucItem): void {
        this.selectedItem = item;
        this.mode = MainView.ItemEdit;
    }

    /**
     * Delete item handler
     * @param item_id Item id
     */
    onSelectDelete(item_id: number): void {
        if (!confirm('Are you sure want to delete this item?')) {
            return;
        }

        this.rpcService.deleteItem(item_id)
            .subscribe(() => this.getItems());
    }

    /**
     * Add new item handler
     */
    onAddNewItem(): void {
        this.selectedItem = {
            title: null,
            description: null,
            price: null,
            close_dt: null
        };
        this.mode = MainView.ItemAddNew;
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
    onItemCardEvent(ev: string) {
        if (ev == ItemCardEvent.NewItemCreated) {
            this.setListViewMode(true);
        } else if (ev ==  ItemCardEvent.ItemCardClosed) {
            this.setListViewMode(true);
        } else if (ev == ItemCardEvent.ItemUpdated) {
            this.setListViewMode(true);
        } else if (ev == ItemCardEvent.ItemNotFound) {
            this.setListViewMode(true);
            this.alertDialog.open('Item not found.');
        }
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
}
