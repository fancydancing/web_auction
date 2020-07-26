import { Injectable } from '@angular/core';
import { CookieService } from 'ngx-cookie-service';
import { DatePipe } from '@angular/common'

import { FormControl, FormGroup } from '@angular/forms';


@Injectable({ providedIn: 'root' })
export class HelpersService {

    constructor(
        private cookieService: CookieService,
        public datepipe: DatePipe
    ) { }

    /**
     * Get formatted datetime string representation
     * @param epoch Epoch secs
     * @param formatting Return string format
     */
    getDateTimeFromEpoch(epoch: number, formatting?: string): string {
        let dt = new Date(0);
        dt.setUTCSeconds(epoch);

        if (!formatting) {
            formatting = 'yyyy-MM-dd HH:mm';
        }

        return this.datepipe.transform(dt, formatting);
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
     * Get current user id from cookie
     * @returns number Current user id
     */
    getUserId(): number {
        return parseInt(this.cookieService.get('auction_user_id'), 10);
    }

    /**
     * Check if current user is admin
     * @returns boolean If current user is admin
     */
    isAdmin(): boolean {
        return this.cookieService.get('auction_role') == 'admin';
    }

    /**
     * Validator for input component. It allows only numbers
     * @param  {} event
     * @returns boolean Is it a number
     */
    numberOnly(event): boolean {
        const charCode = (event.which) ? event.which : event.keyCode;
        if (charCode > 31 && (charCode < 48 || charCode > 57)) {
            return false;
        }
        return true;
    }

    /**
     * Validate whole form
     * @param formGroup form group for validation
     */
    validateAllFormFields(formGroup: FormGroup) {
        Object.keys(formGroup.controls).forEach(field => {
            const control = formGroup.get(field);
            if (control instanceof FormControl) {
                control.markAsTouched({ onlySelf: true });
            } else if (control instanceof FormGroup) {
                this.validateAllFormFields(control);
            }
        });
    }
}
