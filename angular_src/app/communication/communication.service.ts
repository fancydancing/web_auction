import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import { ServerMsg } from '../item';

@Injectable({ providedIn: 'root' })
export class CommunicationService {
    // Observable sources
    private serverMsgAnnouncedSource = new Subject<ServerMsg>();

    private rootMsgAnnouncedSource = new Subject<string>();

    // Observable streams
    serverMsgAnnounced$ = this.serverMsgAnnouncedSource.asObservable();

    rootMsgAnnounced$ = this.rootMsgAnnouncedSource.asObservable();

    // Service message commands
    announceServerMsg(msg: ServerMsg) {
        this.serverMsgAnnouncedSource.next(msg);
    }

    announceRootMsg(msg: string) {
        this.rootMsgAnnouncedSource.next(msg);
    }
}
