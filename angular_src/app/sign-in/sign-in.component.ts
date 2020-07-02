import { Component, OnInit, EventEmitter, Output } from '@angular/core';
import { RpcService } from '../rpc/rpc.service';
import { CookieService } from 'ngx-cookie-service';


@Component({
  selector: 'sign-in',
  templateUrl: './sign-in.component.html',
  styles: []
})
export class SignInComponent implements OnInit {
    login: string;
    password: string;

    @Output() signInEvent: EventEmitter<string> = new EventEmitter<string>();

    constructor(private rpcService: RpcService, private cookieService: CookieService) { }

    ngOnInit() {

    }

    signIn(): void {
        if (!this.login || !this.password) {
            alert('Empty login or password');
            return;
        }

        this.rpcService.signIn(this.login, this.password)
            .subscribe(res => this.signInHandler(res));
    }

    signInHandler(res): void {
        if (res.result == true) {
            this.cookieService.set('auction_user_name', res.login);
            this.cookieService.set('auction_role', res.role);
            this.signInEvent.emit('logged');
        } else {
            alert('Login or Password is incorrect');
        }
    }

}
