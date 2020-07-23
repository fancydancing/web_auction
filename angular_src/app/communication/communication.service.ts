import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import { ServerMsg } from '../item';

@Injectable({ providedIn: 'root' })
export class CommunicationService {
    // Observable sources
    private serverMsgAnnouncedSource = new Subject<ServerMsg>();

    // Observable streams
    serverMsgAnnounced$ = this.serverMsgAnnouncedSource.asObservable();

    // Service message commands
    announceServerMsg(msg: ServerMsg) {
        this.serverMsgAnnouncedSource.next(msg);
    }
}
