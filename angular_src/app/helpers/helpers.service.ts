import { Injectable } from '@angular/core';
import { CookieService } from 'ngx-cookie-service';
import { DatePipe } from '@angular/common'

@Injectable({ providedIn: 'root' })
export class HelpersService {

    constructor(
        private cookieService: CookieService,
        public datepipe: DatePipe
    ) { }

    /**
     * Get formated datetime string representation
     * @param epoch Epoch secs
     * @param formating Return string format
     */
    getDateTimeFromEpoch(epoch: number, formating?: string): string {
        let dt = new Date(0);
        dt.setUTCSeconds(epoch);

        if (!formating) {
            formating = 'yyyy-MM-dd HH:mm';
        }

        return this.datepipe.transform(dt, formating);
    }

    /**
     * Get Date from epoch secs
     * @param epoch Epoch secs
     */
    getDateFromEpoch(epoch: number): Date {
        let dt = new Date(0);
        dt.setUTCSeconds(epoch);
        return dt;
    }

    /**
     * Get epoch secs from datetime
     * @param  {Date} dt Datetime
     * @returns number Epoch secs
     */
    getEpochFromDatetime(dt: Date): number {
        return Math.round(dt.getTime() / 1000);
    }

    /**
     * Get epoch secs of current moment
     * @returns number Epoch secs
     */
    getCurrentEpoch(): number {
        return Math.round(Date.now() / 1000);
    }

    /**
     * Get current user name from cookie
     * @returns string Current user name
     */
    getUserName(): string {
        return this.cookieService.get('auction_user_name');
    }

    /**
     * Check is cuurent user admin
     * @returns boolean Is current user admin
     */
    isAdmin(): boolean {
        return this.cookieService.get('auction_role') == 'admin';
    }

    /**
     * Validator for input component. It allows only numbers
     * @param  {} event
     * @returns boolean Is it number
     */
    numberOnly(event): boolean {
        const charCode = (event.which) ? event.which : event.keyCode;
        if (charCode > 31 && (charCode < 48 || charCode > 57)) {
            return false;
        }
        return true;
    }
}
