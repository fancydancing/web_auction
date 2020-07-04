export interface AucItem {
    id?: number;
    title: string;

    description: string;

    // Item current price (max bid)
    price: number;

    // Item creation epoch time
    create_dt?: number;

    // Item closing epoch time
    close_dt?: number;
}

export interface AucItems {
    // Items list of page
    items?: AucItem[];

    // Total count of items in DB
    total_count?: number;
}

export interface ServerResponse {
    // True - success
    // False - Fail
    result: boolean;

    // Error message
    msg?: string;
}
