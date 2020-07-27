from .models import DeployInfo
from django.db import connection
import random


def deploy_data():
#     sql_str = """
#     UPDATE auction_bid SET user = 1 WHERE user_name = 'admin'
#     UPDATE auction_bid SET user = 2 WHERE user_name = 'user'
#     UPDATE auction_bid SET user = 3 WHERE user_name = 'user2'

#     UPDATE auction_item SET awarded_user_id = 1 WHERE awarded_user = 'admin'
#     UPDATE auction_item SET awarded_user_id = 2 WHERE awarded_user = 'user'
#     UPDATE auction_item SET awarded_user_id = 3 WHERE awarded_user = 'user2'

# """

#     with connection.cursor() as cursor:
#         cursor.execute(sql_str)

    deploy_qs = DeployInfo.objects.filter(deploy_name='initial')
    if len(deploy_qs) > 0:
        return

    sql_str = """
INSERT INTO auction_auctionuser (id, name, password, role, email, autobid_total_sum, autobid_alert_perc) VALUES (1, 'admin', 'admin', 'admin', 'webauctiontesting+admin@gmail.com', null, null);
INSERT INTO auction_auctionuser (id, name, password, role, email, autobid_total_sum, autobid_alert_perc) VALUES (2, 'user', 'user', 'user', 'webauctiontesting+user@gmail.com', null, null);
INSERT INTO auction_auctionuser (id, name, password, role, email, autobid_total_sum, autobid_alert_perc) VALUES (3, 'user2', 'user2', 'user', 'webauctiontesting+user2@gmail.com', null, null);

SELECT pg_catalog.setval('auction_auctionuser_id_seq', 3, true);

INSERT INTO auction_bid (id, user_id, user_name, bid_dt, auto, price, item_id_id) VALUES (1, 1, 'admin', '2020-07-01 17:29:37.486479+00', false, 200, 2);
INSERT INTO auction_bid (id, user_id, user_name, bid_dt, auto, price, item_id_id) VALUES (3, 1, 'admin', '2020-07-02 06:03:56.217496+00', false, 2100, 1);
INSERT INTO auction_bid (id, user_id, user_name, bid_dt, auto, price, item_id_id) VALUES (4, 2, 'user', '2020-07-02 07:11:50.330112+00', false, 215, 2);
INSERT INTO auction_bid (id, user_id, user_name, bid_dt, auto, price, item_id_id) VALUES (5, 1, 'admin', '2020-07-02 08:06:45.802964+00', false, 200, 11);
INSERT INTO auction_bid (id, user_id, user_name, bid_dt, auto, price, item_id_id) VALUES (6, 2, 'user', '2020-07-03 01:48:11.741712+00', false, 1400, 14);
INSERT INTO auction_bid (id, user_id, user_name, bid_dt, auto, price, item_id_id) VALUES (7, 3, 'user2', '2020-07-03 02:25:27.263233+00', false, 4100, 20);
INSERT INTO auction_bid (id, user_id, user_name, bid_dt, auto, price, item_id_id) VALUES (8, 3, 'user2', '2020-07-03 02:27:54.529646+00', false, 3800, 23);
INSERT INTO auction_bid (id, user_id, user_name, bid_dt, auto, price, item_id_id) VALUES (9, 3, 'user2', '2020-07-03 09:35:49.158023+00', false, 600, 21);
INSERT INTO auction_bid (id, user_id, user_name, bid_dt, auto, price, item_id_id) VALUES (10, 3, 'user2', '2020-07-03 09:38:43.374303+00', false, 1150, 15);
INSERT INTO auction_bid (id, user_id, user_name, bid_dt, auto, price, item_id_id) VALUES (11, 1, 'admin', '2020-07-03 18:33:03.673124+00', false, 2200, 26);
INSERT INTO auction_bid (id, user_id, user_name, bid_dt, auto, price, item_id_id) VALUES (12, 1, 'admin', '2020-07-04 09:19:44.914815+00', false, 2050, 27);

SELECT pg_catalog.setval('auction_bid_id_seq', 12, true);

INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (1, 'John Lennon''s broken glasses', '2020-07-01 06:31:21.074002+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 2100, 'Broken glasses from the Beatles frontman');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (2, 'Vintage Louis Vuitton Makeup Case', '2020-07-01 06:32:13.680189+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 215, 'Hard case cosmetic suitcase with Monogram Canvas coating, brass fittings, leather interior, 5 leather loops for bottles. Key attached. Very nice receipt, slight traces of age. 35,5x21,5x26cm.');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (11, 'Link bracelet with rubies, rose cut diamonds and enamel', '2020-07-02 07:55:14.019906+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 200, 'India, Rajasthan, 1850 yellow gold 22 ct., tested. Translucent enamel in blue, red, green, and white hues. 48 tiny rose cut diamonds, together CA. 0,30 ct. 12 rubies, round cabochon cut, together approx 0,45 ct. L. approx. 19 cm, width approx 1.5 cm. About 54,6 g.');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (12, 'Pierced bowl made of silver with a dragon decor', '2020-07-02 08:24:29.491926+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 1300, 'Crafted shell made of silver, pierced with dragon decoration and Voalkartuschen. CHINA, u. a. hallmarked WH (Wang Hing) 90, late Qing dynasty. B. 25.1 cm/734 g');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (13, 'Set for spices "Atkin Brothers". England, crystal, silver, handmade, 1853-1925 years.', '2020-07-02 08:24:49.198837+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 120, 'Serving set for spices of the Victorian era. Containers for spices is made of crystal glass with low lead content and faceted by hand. Base, spoon and lid Nickel alloy plated with 925 silver.');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (14, 'Porcelain figurine "Parrot". Germany, Sitzendorf, handmade, 1918-1949gg.', '2020-07-02 08:25:17.47955+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 1400, 'Porcelain figurine of a parrot sitting on a tree. Completely handmade.');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (16, 'Porcelain figurines "Henry VIII and his wives". Germany, Sitzendorf, handmade, 1918 - 1949 gg.', '2020-07-02 08:26:13.451883+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 1350, 'Full collection of seven porcelain figurines of Henry VIII and his wives. Completely handmade.');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (17, 'Jug Wedgwood "Meander". Neo-classicism, England, biscuit porcelain, 1860-1891 years.', '2020-07-02 08:26:36.98427+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 160, 'Jug of porcelain Jasper with silver plated lid by the iconic British company Wedgwood. Fully handmade');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (18, 'Moscow. Cigarette case with niello, 84 sample.', '2020-07-02 08:28:14.558242+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 1000, 'Cigarette case depicting Moscow Kremlin.');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (20, 'The sculpture "bear lying".', '2020-07-02 12:26:23.740808+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 4100, 'Russia, 19th century. Bronze, casting, embossing, Druse quartz.');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (22, 'Figurine "Chick". China, enamel, handmade', '2020-07-02 12:32:31.646369+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 80, 'Figurine chicken cloisonné enamel Cloisonne. Included - individual stand of lacquered wood. Handmade.');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (23, 'Saber Dragoon officer sample 1881/1909 year', '2020-07-02 15:15:58.211817+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 3800, 'Efes consists of a handle and brass guard. The handle is wooden, sometimes ebony, with deep transverse grooves and thickening in the middle part. At the top on the handle, notched brass bushing, on top of her oval head is in the form of a rosette.');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (21, 'Porcelain composition "Pigeon mail", Germany, Sitzendorf, 19th century, handmade', '2020-07-02 12:26:23.327433+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 600, 'Porcelain figurine - a pair with the carrier pigeons. Completely handmade.');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (15, 'Antique carafe, decanter, bottle, England, Glass, first half 20th century, handmade', '2020-07-02 08:25:48.059775+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 1150, 'Decanter for liqueurs and bitters. The vessel is decorated with patterns applied by engraving. Completely handmade.');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (24, 'Decorative vase, rare technique of stained glass enamels', '2020-07-03 18:02:24.937743+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 277, 'Vase, made in a rare technique of stained enamel and Plique-à-jour (FR. "let in daylight"). It is a technique of enameling in which enamel is put in the cells, similar to cloisonne, the only difference is that uses a temporary basis, which after firing is dissolved by acid.');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (25, 'Saucer for jewelry Wedgwood "Orchids". Neo-classicism, England, biscuit porcelain. 1974 - 1990', '2020-07-03 18:10:18.868625+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 49, 'Saucer for decorations of porcelain Jasper from the iconic British company Wedgwood in rare colors. All items are carved from porcelain by hand');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (26, 'Desktop device of "Horse"', '2020-07-03 18:12:40.586611+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 2200, 'Desktop device of "Horse". Includes pencil holders, a box. there is a plaque with the inscription in Georgian, dated 1935.');
INSERT INTO auction_item (id, title, create_dt, close_dt, price, description) VALUES (27, 'Fireplace set in the art Nouveau style', '2020-07-04 09:04:43.528714+00', now() + interval '""" + str(random.randint(1, 120)) + """ hour', 2050, 'Fireplace set, consisting of a clock and pair of vases. Items decorated with images of cyclamen and floral ornament in art Nouveau style. ');

SELECT pg_catalog.setval('auction_item_id_seq', 27, true);
"""
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
    DeployInfo.objects.create(deploy_name='initial')
