export interface AucItem {
    id?: number;
    title: string;
    description: string;
    price: number;
    create_dt?: number;
    close_dt?: number;
}

export interface AucItems {
    items?: AucItem[];
    total_count?: number;
}
