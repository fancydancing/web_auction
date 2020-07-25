export interface AucItem {
    id?: number;
    title?: string;

    description?: string;

    // Item current price (max bid)
    price?: number;

    // Item creation epoch time
    create_dt?: number;

    // Item closing epoch time
    close_dt?: number;

    awarded_user?: string;

    expired?: boolean;
}

export interface AucUserItem {
    item_id?: number;
    item?: string;
    dt?: number;
    close_dt?: number;
    status?: string;
    user_price?: number;
    max_price?: number;
}

export interface UserInfo {
    id?: number;
    name?: string;
    email?: string;
    autobid_total_sum?: number;
    autobid_alert_perc?: number;
}

export interface AucItems {
    // Items list of page
    items?: AucItem[];

    // Total count of items in DB
    total_count?: number;
}

export interface Bid {
    // Bid unique id
    id?: number;

    // Bid price
    price: number;

    // User name of bid
    user_name: string;

    // Epoch datetime of bid creation
    bid_dt: number;
}


export interface ServerResponse {
    // True - success
    // False - Fail
    result: boolean;

    // Error message
    msg?: string;
}

export enum MainView {
    List = 'list_view', // show list of items
    Item = 'item_view', // show item card
    ItemEdit = 'item_edit', // show item card in edit mode
    ItemAddNew = 'add_new_item' // show new empty item card in edit mode
}

export enum ItemCardEvent {
    // Events from card to parent list

    NewItemCreated = 'new_item_created',
    ItemCardClosed = 'item_card_closed',
    ItemUpdated = 'item_updated',
    ItemNotFound = 'item_not_found', // show dialog: item not found
}

export interface ServerMsg {
    item_id?: number;

    event?: string;

    user_id?: number;

    item_title?: string;
}
