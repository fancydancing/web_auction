import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { AucItem } from '../item';
import { RpcService } from '../rpc/rpc.service';
import { HelpersService } from '../helpers/helpers.service';

import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

import { ViewChild, AfterViewInit} from '@angular/core';
import {MatPaginator} from '@angular/material/paginator';
import {MatSort} from '@angular/material/sort';
import {merge, Observable, of as observableOf} from 'rxjs';
import { catchError, map, startWith, switchMap, delay } from 'rxjs/operators';


@Component({
  selector: 'items-list',
  templateUrl: './items-list.component.html',
  styles: [],
  encapsulation: ViewEncapsulation.None
})
export class ItemsListComponent implements AfterViewInit  {
    items: AucItem[];
    selectedItem: AucItem;
    mode: String = 'list_view';
    search_string: String = null;
    is_admin: boolean = false;

    searchTerms: Subject<string> = new Subject<string>();

    displayedColumns: string[] = ['title', 'price', 'create_dt'];
    resultsLength = 0;

    @ViewChild(MatPaginator) paginator: MatPaginator;
    @ViewChild(MatSort) sort: MatSort;

    constructor(private rpcService: RpcService, public helpersService: HelpersService) {
        this.is_admin = this.helpersService.isAdmin();

        if (this.is_admin) {
            this.displayedColumns.push('operations');
        }
    }

    ngAfterViewInit() {
         // If the user changes the sort order, reset back to the first page.
        this.sort.sortChange.subscribe(() => this.paginator.pageIndex = 0);

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

    startSearch(term: string): void {
        this.search_string = term;
        this.getItems();
    }

    search(term: string): void {
        // Push a search term into the observable stream.
        this.searchTerms.next(term);
    }

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

    handleResult(data) {
        this.resultsLength = data.total_count;
        this.items = data.items;
    }

    onSelect(item: AucItem): void {
        this.selectedItem = item;
        this.mode = 'item_view';
    }

    onSelectEdit(item: AucItem): void {
        this.selectedItem = item;
        this.mode = 'item_edit';
    }

    onSelectDelete(item_id: number): void {
        if (!confirm('Are you sure want to delete this item?')) {
            return;
        }

        this.rpcService.deleteItem(item_id)
            .subscribe(() => this.getItems());
    }

    onAddNewItem(): void {
        this.selectedItem = {
            title: null,
            description: null,
            price: null,
            close_dt: null
        };
        this.mode = 'add_new_item';
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
            this.setListViewMode(true);
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
