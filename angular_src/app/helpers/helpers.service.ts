import { Injectable } from '@angular/core';
import { CookieService } from 'ngx-cookie-service';
import { DatePipe } from '@angular/common'

@Injectable({ providedIn: 'root' })
export class HelpersService {

    constructor(private cookieService: CookieService, public datepipe: DatePipe) { }

    getDateTimeFromEpoch(epoch: number): String {
        let dt = new Date(0);
        dt.setUTCSeconds(epoch);
        return this.datepipe.transform(dt, 'yyyy-MM-dd HH:mm');
    }

    getUserName(): string {
        return this.cookieService.get('auction_user_name');
    }

    isAdmin(): boolean {
        return this.cookieService.get('auction_role') == 'admin';
    }
}
