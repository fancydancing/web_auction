import { Injectable } from '@angular/core';
import { CookieService } from 'ngx-cookie-service';
import { DatePipe } from '@angular/common'

@Injectable({ providedIn: 'root' })
export class HelpersService {

    constructor(private cookieService: CookieService, public datepipe: DatePipe) { }

    getDateTimeFromEpoch(epoch: number, formating?: string): String {
        let dt = new Date(0);
        dt.setUTCSeconds(epoch);

        if (!formating) {
            formating = 'yyyy-MM-dd HH:mm';
        }

        return this.datepipe.transform(dt, formating);
    }

    getUserName(): string {
        return this.cookieService.get('auction_user_name');
    }

    isAdmin(): boolean {
        return this.cookieService.get('auction_role') == 'admin';
    }

    numberOnly(event): boolean {
        const charCode = (event.which) ? event.which : event.keyCode;
        if (charCode > 31 && (charCode < 48 || charCode > 57)) {
            return false;
        }
        return true;
    }
}
