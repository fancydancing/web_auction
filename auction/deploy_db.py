from .models import DeployInfo
from django.db import connection


def deploy_data():
    deploy_qs = DeployInfo.objects.filter(deploy_name='initial')
    if len(deploy_qs) > 0:
        return

    sql_str = """
INSERT INTO auction_bid (id, user_name, bid_dt, price, item_id_id) VALUES (1, 'admin', '2020-07-01 17:29:37.486479+00', 5, 2);
INSERT INTO auction_bid (id, user_name, bid_dt, price, item_id_id) VALUES (2, 'admin', '2020-07-02 05:51:37.621245+00', 10, 2);
INSERT INTO auction_bid (id, user_name, bid_dt, price, item_id_id) VALUES (3, 'admin', '2020-07-02 06:03:56.217496+00', 1000, 1);
INSERT INTO auction_bid (id, user_name, bid_dt, price, item_id_id) VALUES (4, 'user', '2020-07-02 07:11:50.330112+00', 9, 2);
INSERT INTO auction_bid (id, user_name, bid_dt, price, item_id_id) VALUES (5, 'admin', '2020-07-02 08:06:45.802964+00', 200, 11);
INSERT INTO auction_bid (id, user_name, bid_dt, price, item_id_id) VALUES (6, 'user', '2020-07-03 01:48:11.741712+00', 3, 16);
INSERT INTO auction_bid (id, user_name, bid_dt, price, item_id_id) VALUES (7, 'user2', '2020-07-03 02:25:27.263233+00', 12, 20);
INSERT INTO auction_bid (id, user_name, bid_dt, price, item_id_id) VALUES (8, 'user2', '2020-07-03 02:27:54.529646+00', 20, 23);
INSERT INTO auction_bid (id, user_name, bid_dt, price, item_id_id) VALUES (9, 'user2', '2020-07-03 09:35:49.158023+00', 11, 21);
INSERT INTO auction_bid (id, user_name, bid_dt, price, item_id_id) VALUES (10, 'user2', '2020-07-03 09:38:43.374303+00', 350, 15);
INSERT INTO auction_bid (id, user_name, bid_dt, price, item_id_id) VALUES (11, 'admin', '2020-07-03 18:33:03.673124+00', 25, 26);
INSERT INTO auction_bid (id, user_name, bid_dt, price, item_id_id) VALUES (12, 'admin', '2020-07-04 09:19:44.914815+00', 0, 27);

SELECT pg_catalog.setval('auction_bid_id_seq', 12, true);

INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (0, 'Golden watch', '2020-07-01 06:30:26.112461+00', '2020-07-01 06:30:26.112461+00', 3, 'Best golden watch in the whole world!!1!11');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (1, 'John Lennon''s broken glasses', '2020-07-01 06:31:21.074002+00', '2020-07-01 06:31:21.074002+00', 2000, 'Broken glasses from the Beatles frontman');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (2, 'Lord of the rings75', '2020-07-01 06:32:13.680189+00', '2020-07-30 06:32:13+00', 20, 'The Fellowship of the Ring');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (11, 'Harry Potter222', '2020-07-02 07:55:14.019906+00', '2012-09-13 11:22:50+00', 101, 'by J K Rowling');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (12, 'Alphabet 123', '2020-07-02 08:24:29.491926+00', '2012-09-13 11:22:50+00', 123, 'junior and senior');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (13, 'Ololo', '2020-07-02 08:24:49.198837+00', '2012-09-13 11:22:50+00', 14, 'ewrv mfegl');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (14, 'Voyna i mir', '2020-07-02 08:25:17.47955+00', '2012-09-13 11:22:50+00', 500, 'Tolstoy author edition');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (16, 'Proschanie c Materoy', '2020-07-02 08:26:13.451883+00', '2012-09-13 11:22:50+00', 1, 'dont remember');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (17, '10th Kingdom', '2020-07-02 08:26:36.98427+00', '2012-09-13 11:22:50+00', 12, 'desyatoe');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (18, 'Buratino', '2020-07-02 08:28:14.558242+00', '2012-09-13 11:22:50+00', 122, 'Alexey Tolstoy');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (20, 'Will delete', '2020-07-02 12:26:23.740808+00', '2020-07-21 17:26:10+00', 10, 'today tomorrow always');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (22, 'Check', '2020-07-02 12:32:31.646369+00', '2020-07-13 17:32:23+00', 234, 'chekersson');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (23, 'Moby Dick', '2020-07-02 15:15:58.211817+00', '2020-07-23 20:15:32+00', 20, 'Melvill Hall');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (21, 'Will delete', '2020-07-02 12:26:23.327433+00', '2020-07-21 17:26:10+00', 11, 'today tomorrow always');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (15, 'Master & Margarita', '2020-07-02 08:25:48.059775+00', '2012-09-13 11:22:50+00', 350, 'Bulghakov');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (24, 'Livin'' In The Ghost Town', '2020-07-03 18:02:24.937743+00', '2020-07-08 23:02:14+00', 356, 'Rolling Stones');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (25, 'Mad World', '2020-07-03 18:10:18.868625+00', '2020-07-12 23:10:05+00', 1000, 'Donnie Darko Theme');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (26, 'Lonely Day', '2020-07-03 18:12:40.586611+00', '2020-07-22 23:12:30+00', 25, 'SOAD');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (27, 'Imagine', '2020-07-04 09:04:43.528714+00', '2020-07-23 14:04:36+00', -3, 'John Lennon');

SELECT pg_catalog.setval('auction_item_id_seq', 27, true);
"""
    with connection.cursor() as cursor:
        cursor.execute(sql_str)    
    DeployInfo.objects.create(deploy_name='initial')
