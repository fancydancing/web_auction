import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';

import { CookieService } from 'ngx-cookie-service';

import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { AucItem, AucItems, ServerResponse, Bid, AucUserItem, UserInfo, UserItem } from '../item';


@Injectable({ providedIn: 'root' })
export class RpcService {

    httpOptions = {
        headers: new HttpHeaders({ 'Content-Type': 'application/json' })
    };

    constructor(private http: HttpClient, private cookieService: CookieService) { }


    /**
     * Get items from backend
     * @param params Set of filters
     */
    getItems(params): Observable<AucItems> {
        let ps = {
            'page': params.page ? params.page : 0,
            'sort': params.sort ? params.sort : 'create_dt',
            'order': params.order ? params.order : 'desc',
            'show_closed': params.show_closed
        };

        if (params.page_size) {
            ps['page_size'] = params.page_size;
        }

        if (params.search_string) {
            ps['search_string'] = params.search_string;
        }

        let itemsUrl = 'api/items';
        return this.http.get<AucItems>(itemsUrl, { params: ps })
            .pipe(
                catchError(this.handleError<AucItems>('getItems', {}))
            );
    }

    /**
     * Get user bids from backend
     * @param  {} params Set of filters
     */
    getUserItems(params): Observable<AucUserItem[]> {
        let user_name = this.cookieService.get('auction_user_name');

        let ps = {
            'user': user_name,
            'sort': params.sort ? params.sort : 'close_dt',
            'status': null
        };

        if (params.status) {
            ps['status'] = params.status;
        }

        let itemsUrl = 'api/users/bids';
        return this.http.get<AucUserItem[]>(itemsUrl, { params: ps })
            .pipe(
                catchError(this.handleError<AucUserItem[]>('getUserItems', []))
            );
    }

    /**
     * Get bids list of item from backend
     * @param item_id Item id
     */
    getBids(item_id: Number): Observable<Bid[]> {
        const url = `api/items/${item_id}/bids`

        return this.http.get<Bid[]>(url)
            .pipe(
                catchError(this.handleError<Bid[]>('getBids', []))
            );
    }

    /**
     * Get item from backend
     * @param item_id Item id
     */
    getItem(item_id: Number): Observable<AucItem> {
        const url = `api/items/${item_id}`;
        return this.http.get<AucItem>(url)
            .pipe(
                catchError(this.handleError<AucItem>('getItem', null))
            );
    }

    /**
     * Read user info
     * @param  {Number} user_id User ID
     */
    getUser(user_id: Number): Observable<UserInfo> {
        const url = `api/users/${user_id}`;
        return this.http.get<UserInfo>(url)
            .pipe(
                catchError(this.handleError<UserInfo>('getUser', null))
            );
    }

    /**
     * Get infor about user bids on an item
     * @param  {Number} user_id User ID
     * @param  {Number} item_id Item ID
     */
    getUserItemInfo(user_id: Number, item_id: Number): Observable<UserItem> {
        const url = `api/users/${user_id}/item/${item_id}`;
        return this.http.get<UserItem>(url)
            .pipe(
                catchError(this.handleError<UserItem>('getUserItemInfo', null))
            );
    }

    /**
     * Add new item to backend
     * @param item
     */
    addItem(item: AucItem): Observable<{}> {
        const url = 'api/items';
        return this.http.post(url, item)
            .pipe(
                catchError(this.handleError('addItem'))
            );
    }

    /**
     * Send new bid to backend
     * @param item_id Item id
     * @param bid_price Item bid price in $
     */
    makeBid(item_id: number, bid_price: number): Observable<ServerResponse> {
        let user_name = this.cookieService.get('auction_user_name');

        const url = `api/items/${item_id}/bids`;
        return this.http.post<ServerResponse>(url, {price: bid_price, user_name: user_name})
            .pipe(
                catchError(this.handleError<ServerResponse>('makeBid'))
            );
    }

    /**
     * Enable or disable autobid option
     * @param  {number} item_id Item ID
     * @param  {number} user_id User ID
     * @param  {boolean} auto_bid Enable/disable autobid
     */
    autoBid(item_id: number, user_id: number, auto_bid: boolean): Observable<ServerResponse> {
        const url = `api/items/${item_id}/auto_bid`;
        return this.http.post<ServerResponse>(url, {auto_bid: auto_bid, user_id: user_id})
            .pipe(
                catchError(this.handleError<ServerResponse>('autoBid'))
            );
    }

    /**
     * Update item
     * @param item Item data
     */
    updateItem(item: AucItem): Observable<{}> {
        const url = 'api/items/' + item.id.toString(10);
        return this.http.put(url, item, this.httpOptions)
            .pipe(
                catchError(this.handleError('updateItem'))
            );
    }

    /**
     * Update user settings
     * @param  {UserInfo} userInfo User settings
     */
    updateUserInfo(userInfo: UserInfo): Observable<{}> {
        const url = 'api/users/' + userInfo.id.toString(10);
        return this.http.put(url, userInfo, this.httpOptions)
            .pipe(
                catchError(this.handleError('updateUserInfo'))
            );
    }

    /**
     * Delete item
     * @param item_id Item id
     */
    deleteItem(item_id: number): Observable<{}> {
        const url = `api/items/${item_id}`;
        return this.http.delete(url, this.httpOptions)
            .pipe(
                catchError(this.handleError('deleteItem'))
            );
    }

    /**
     * Sign in attempt
     * @param login Login
     * @param password Password
     */
    signIn(login: String, password: String): Observable<{}> {
        const url = 'api/sign_in';
        return this.http.post(url, {login: login, password: password})
            .pipe(
                catchError(this.handleError('makeBid'))
            );
    }

    /**
     * Handle Http operation that failed.
     * Let the app continue.
     * @param operation name of the operation that failed
     * @param result optional value to return as the observable result
     */
    private handleError<T>(operation = 'operation', result?: T) {
        return (error: any): Observable<T> => {
            console.error(error);

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }
}
