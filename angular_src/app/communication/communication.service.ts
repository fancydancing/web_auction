import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import { ServerMsg } from '../item';

@Injectable({ providedIn: 'root' })
export class CommunicationService {
    // Observable source of websockets messages
    private serverMsgAnnouncedSource = new Subject<ServerMsg>();

    // Observable source of global frontend messages
    private rootMsgAnnouncedSource = new Subject<string>();

    // Observable stream of websockets messages
    serverMsgAnnounced$ = this.serverMsgAnnouncedSource.asObservable();

    // Observable stream of global frontend messages
    rootMsgAnnounced$ = this.rootMsgAnnouncedSource.asObservable();

    // Broadcast websocket message
    announceServerMsg(msg: ServerMsg) {
        this.serverMsgAnnouncedSource.next(msg);
    }

    // Broadcast frontend message
    announceRootMsg(msg: string) {
        this.rootMsgAnnouncedSource.next(msg);
    }
}
