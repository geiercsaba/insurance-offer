class Customer:
    def __init__(self):
        self.id = None
        self.company_name = None
        self.address = None
        self.tax_number = None
        self.registration_number = None
        self.payment_frequency = None

        self.broker = None
        self.email = None

        self.cmr = False
        self.baf = False

        self.groups = []

    def customer_form_json(self, customer, groups):
        self.id = customer["id"]
        self.company_name = customer["company_name"]
        self.address = customer["address"]
        self.tax_number = customer["tax_number"]
        self.registration_number = customer["registration_number"]
        self.payment_frequency = customer["payment_frequency"]
        self.broker = customer["broker"]
        self.email = customer["email"]

        for group in groups:
            new_group = Group()
            # adatok feltöltése a csoportba:
            new_group.number_of_trucks = int(group["number_of_trucks"])
            new_group.cmr_limit = int(group["cmr_limit"])
            if new_group.cmr_limit != 0:
                new_group.cmr = True
                self.cmr = True
            new_group.baf_limit = int(group["baf_limit"])
            if new_group.baf_limit != 0:
                self.baf = True
                new_group.baf = True
            new_group.cabotage = group["cabotage"]
            new_group.group_number = group["group_number"]
            # záradékok feltöltése
            cmr_claus = group["cmr_clauses"]
            for i in range(len(new_group.cmr_clauses)):
                if cmr_claus[i] == "1":
                    new_group.cmr_clauses[i][2] = True

            baf_claus = group["baf_clauses"]
            for i in range(len(new_group.baf_clauses)):
                if baf_claus[i] == "1":
                    new_group.baf_clauses[i][2] = True

            # díjkalkuláció
            new_group.calculator()
            self.groups.append(new_group)

    def get_data(self):
        def format_string(txt):
            return '{:,}'.format(txt).replace(',', ' ')

        def list_to_string(lista):
            txt = ""
            for elem in lista:
                if txt:
                    txt += "\n"
                txt += elem
            return txt

        def add_to_dict(my_dict: dict, new_key: str, new_value: str, duplicate=False):
            new_key = f"{new_key}."
            if duplicate or (new_value not in my_dict.values()):
                my_dict[new_key] = new_value
            else:
                old_key = [key for key, value in my_dict.items() if value == new_value][0]
                my_dict[old_key + " és " + new_key] = new_value
                del my_dict[old_key]
            return my_dict

        def get_string(my_dict: dict):
            if len(my_dict) == 1:
                key, value = next(iter(my_dict.items()))
                return value
            else:
                returned_string = ""
                for key, value in my_dict.items():
                    returned_string += f"{key} csoport: {value}\n"
            return returned_string[:-1]

        def get_limits(lim, cmr_lim, baf_lim):
            sublimit = list_to_string(lim)

            cmr_max = max(cmr_lim.values(), default=0)
            baf_max = max(baf_lim.values(), default=0)

            maximum = cmr_max if cmr_max * 400 > baf_max else baf_max
            cmr = True if maximum == cmr_max else False

            comb_limit = f"a CMR Egyezményben foglaltaknak megfelelően a hiányzó, illetve sérült " \
                         f"áru bruttó súlya szerint kilogrammonként max. 8,33 SDR de mindösszesen maximum:" \
                         f"\nEUR {format_string(cmr_max)} / káresemény / év" if cmr else f"belföldi fuvarozás során okozott károkra:\n{format_string(maximum)},-Ft / káresemény / év"

            for key, value in cmr_lim.items():
                if value != maximum or not cmr:
                    if not sublimit:
                        sublimit += "\n"
                    sublimit += f"{key} csoport: a CMR Egyezményben foglaltaknak megfelelően a hiányzó, " \
                                f"illetve sérült áru bruttó súlya szerint kilogrammonként max. 8,33 SDR " \
                                f"de mindösszesen maximum:\nEUR {format_string(value)} / " \
                                f"káresemény / év"

            for key, value in baf_lim.items():
                if value != maximum or cmr:
                    sublimit += f"\n{key} csoport: belföldi fuvarozás során okozott károkra: " \
                                f"\n{format_string(value)},-Ft / káresemény / év"

            return comb_limit, sublimit

        sublimit_txt_1 = "Hibás lefejtésből eredő károkra\n1 000 000,-Ft / káresemény / év"
        sublimit_txt_2 = "Konténerek káraira\n1 000 000,-Ft / káresemény / év"

        additional_txt_1 = "A fedezet kiterjed a nyitott szállítóeszközökkel történő fuvarozás során bekövetkező károkra, de nem terjed ki az ilyen szállításokkal szükségképpen együttjáró veszélyek (jégeső, felhőszakadás, nedvesedés stb.) eredményeként bekövetkező károkra, és a nyitott szállítóeszközökkel történő fuvarozás során bekövetkező hiánykárokra (lopás, rablás vagy bármilyen okból bekövetkezett áruhiány)"
        additional_txt_2 = "E záradék alkalmazásával a biztosító kockázatviselése és a biztosítási fedezet kiterjed a dohánytermékekre is. E záradék által nyújtott fedezet azonban nem terjed ki a károsodott illetve elveszett áruk jövedéki adótartamára\nE záradék alapján a biztosítási fedezet fennállásának további feltétele, hogy a biztosított az általános és különös biztosítási feltételekben foglaltak mellett az alábbi együttes előírásokat is betartja: \n- A tehergépjárművek GPS rendszerrel (24 órás követés, állandó on-line kapcsolat a távfelügyeleti központtal, jelkimaradás figyelése, adatmentés, min. 30 napos adattárolás) és működő mobiltelefonnal felszereltek.\n- A megbízó fuvarfeladattal kapcsolatos mindennemű előírását kötelezően be kell tartani.\n- Kizárólag a megbízó által adott előírásoknak megfelelő védelmi szintű, vagy a megbízó által külön listában meghatározott parkolókban állhatnak meg. (Ez az AETR megállapodás szerinti pihenőidőkre és szünetekre egyaránt alkalmazandó.)\n- Amennyiben a megbízó nem határozott meg követelményeket az igénybe vehető parkolókra vonatkozóan, vagy nem írta elő meghatározott parkolók használatát, abban az esetben kizárólag kivilágított, körbekerített, kamerával vagy emberi erővel őrzött parkolók vehetők igénybe. (Ez az AETR megállapodás szerinti pihenőidőkre és szünetekre egyaránt alkalmazandó.)\n- Ha a tervezett kiszolgáltatás meghiúsul, az új kiszolgáltatási időpontig kizárólag kivilágított, körbekerített, kamerával vagy emberi erővel őrzött parkolók vehetők igénybe.\n- A szállítás teljes tartama alatt zárva kell tartani a rakteret.\n- A pótkocsikon nem lehet semmilyen jelzés, utalás a szállított árura vonatkozóan.\n- Amennyiben a fuvarozás két sofőrrel történik,  az egyik gépjárművezetőnek mindig az autóban kell tartózkodnia.\n- A fuvarfeladatot teljesítő gépjárművezetőnek / gépjárművezetőknek legalább 3 hónapos munkaviszonnyal kell rendelkezni a biztosítottnál\n- A gépjárművezető kiszolgáltatás során köteles ellenőrizni, hogy a fuvarlevélen vagy szállítólevélen megjelölt címzett neve szerinti bélyegzőt használtak–e átvételkor. Eltérés esetén a biztosított még a kiszolgáltatás befejezése, illetve a helyszín elhagyása előtt köteles a megbízóval egyeztetni az eltérést és az egyeztetés eredményét írásban is megküldeni a megbízó részére.\nA dohányárukban keletkezett károkra az önrészesedés mértéke 20%, de minimum 100 000 Ft"
        additional_txt_3 = "E záradék alapján a biztosítási fedezet fennállásának további feltétele, hogy a biztosított az általános és különös biztosítási feltételekben foglaltak mellett az alábbi együttes előírásokat is betartja: \n- A tehergépjárművek GPS rendszerrel (24 órás követés) és működő mobiltelefonnal felszereltek.\n- A megbízó fuvarfeladattal kapcsolatos mindennemű előírását kötelezően be kell tartani. \n- Kizárólag a megbízó által adott előírásoknak megfelelő védelmi szintű vagy a megbízó által külön listában meghatározott – de minimum kivilágított, körbekerített, kamerával vagy emberi erővel őrzött - parkolókban állhatnak meg. (Az AETR megállapodás szerinti pihenőidőkre és szünetekre egyaránt alkalmazandó.) \n- Amennyiben a megbízó nem határozott meg követelményeket az igénybe vehető parkolókra vonatkozóan, vagy nem írta elő meghatározott parkolók használatát, abban az esetben kizárólag kivilágított, körbekerített, kamerával vagy emberi erővel őrzött parkolók vehetők igénybe. (Az AETR megállapodás szerinti pihenőidőkre és szünetekre egyaránt alkalmazandó.) \n- Ha a tervezett kiszolgáltatás meghiúsul, az új kiszolgáltatási időpontig kizárólag kivilágított, körbekerített, kamerával vagy emberi erővel őrzött parkolók vehetők igénybe. \n- A szállítás teljes tartama alatt zárva kell tartani a rakteret. \n- A pótkocsikon nem lehet semmilyen jelzés, utalás a szállított árura vonatkozóan. \n- Két gépjárművezetővel végzett fuvarozás esetén az egyik gépjárművezetőnek mindig az autóban kell tartózkodnia. \n- A fuvarfeladatot teljesítő gépjárművezetőnek / gépjárművezetőknek legalább 3 hónapos munkaviszonnyal kell rendelkezni a biztosítottnál. \n- A gépjárművezető az áru kiszolgáltatása során köteles ellenőrizni, hogy a fuvarlevélen illetőleg szállítólevélen megjelölt címzett neve szerinti bélyegzőt használtak–e átvételkor. Eltérés esetén a biztosított még a kiszolgáltatás befejezése, illetve a helyszín elhagyása előtt köteles az eltérést a megbízóval egyeztetni és az egyeztetés eredményét írásban is megküldeni a megbízó részére."
        additional_txt_4 = "E záradék alkalmazásával a biztosító kockázatviselése és a biztosítási fedezet kiterjed a mobiltelefonok fuvarozására az alábbi biztonsági előírások betartásával\nA biztosítási fedezet mobiltelen szállításokra csak akkor él, ha a Biztosított a feltételekben foglaltakon kívül az alábbi biztonsági utasításokat is betartja:\n- kizárólag dobozos kamionnal lehet szállítani\n- a járművek rögzített biztonsági raktérzárral ellátottak (SBS speciális lakat)\n- A tehergépjárművek (vontató és pótkocsi is)  GPS rendszerrel (24 órás követés, állandó on-line kapcsolat a távfelügyeleti központtal, jelkimaradás figyelése, adatmentés, min. 30 napos adattárolás) és működő mobiltelefonnal felszereltek.\n- Kizárólag a megbízó által adott előírásoknak megfelelő védelmi szintű, vagy a megbízó által külön listában meghatározott parkolókban állhatnak meg. (Ez az AETR megállapodás szerinti pihenőidőkre és szünetekre egyaránt alkalmazandó.)\n- Amennyiben a megbízó nem határozott meg követelményeket az igénybe vehető parkolókra vonatkozóan, vagy nem írta elő meghatározott parkolók használatát, abban az esetben kizárólag kivilágított, körbekerített, kamerával vagy emberi erővel őrzött parkolók vehetők igénybe. (Ez az AETR megállapodás szerinti pihenőidőkre és szünetekre egyaránt alkalmazandó.)\n- Ha a tervezett kiszolgáltatás meghiúsul, az új kiszolgáltatási időpontig kizárólag kivilágított, körbekerített, kamerával vagy emberi erővel őrzött parkolók vehetők igénybe.\n- kizárólag a megbízók által megadott útvonalon haladhatnak a járművek, \n- a szállítás teljes tartama alatt zárva kell tartani a rakteret\n- a kiszállítási címek előtt tilos várakozni\n- a pótkocsikon nem lehet semmilyen jelzés, utalás a szállított árura vonatkozóan\n- kizárólag két sofőrrel lehet szállítani, az egyik sofőrnek mindig az autóban kell tartózkodnia\n- a sofőröknek minimum 6 hónapos munkaviszonnyal kell rendelkezni a Szerződőnél\n- a megbízók biztonsági vonatkozó előírásait kötelezően be kell tartani\n- a gépjárművezető kiszolgáltatás során köteles ellenőrizni, hogy a CMR fuvarlevélen megjelölt címzett neve szerinti bélyegzőt használtak –e átvételkor. Eltérés esetén a megbízóval a szerződő kiszolgáltatás előtt köteles egyeztetni ezt dokumentálni."
        additional_txt_5 = "E záradék alkalmazásával a biztosító kockázatviselése és a biztosítási fedezet kiterjed a szeszes ital árukra is. E záradék által nyújtott fedezet azonban nem terjed ki a károsodott illetve elveszett áruk jövedéki adótartamára \nE záradék alapján a biztosítási fedezet fennállásának további feltétele, hogy a biztosított az általános és különös biztosítási feltételekben foglaltak mellett az alábbi együttes előírásokat is betartja: \n- A tehergépjárművek GPS rendszerrel (24 órás követés) és működő mobiltelefonnal felszereltek. \n- A megbízó fuvarfeladattal kapcsolatos mindennemű előírását kötelezően be kell tartani.\n - Kizárólag a megbízó által adott előírásoknak megfelelő védelmi szintű, vagy a megbízó által külön listában meghatározott parkolókban állhatnak meg. (Ez az AETR megállapodás szerinti pihenőidőkre és szünetekre egyaránt alkalmazandó.) \n- Amennyiben a megbízó nem határozott meg követelményeket az igénybe vehető parkolókra vonatkozóan, vagy nem írta elő meghatározott parkolók használatát, abban az esetben kizárólag kivilágított, körbekerített, kamerával vagy emberi erővel őrzött parkolók vehetők igénybe. (Ez az AETR megállapodás szerinti pihenőidőkre és szünetekre egyaránt alkalmazandó.) \n- Ha a tervezett kiszolgáltatás meghiúsul, az új kiszolgáltatási időpontig kizárólag kivilágított, körbekerített, kamerával vagy emberi erővel őrzött parkolók vehetők igénybe. \n- A szállítás teljes tartama alatt zárva kell tartani a rakteret. \n- A pótkocsikon nem lehet semmilyen jelzés, utalás a szállított árura vonatkozóan. \n- Két gépjárművezetővel végzett fuvarozás esetén az egyik gépjárművezetőnek mindig az autóban kell tartózkodnia. \n- A fuvarfeladatot teljesítő gépjárművezetőnek / gépjárművezetőknek legalább 3 hónapos munkaviszonnyal kell rendelkezni a biztosítottnál. \n- A gépjárművezető kiszolgáltatás során köteles ellenőrizni, hogy a fuvarlevélen megjelölt címzett neve szerinti bélyegzőt használtak–e átvételkor. Eltérés esetén a biztosított még a kiszolgáltatás befejezése, illetve a helyszín elhagyása előtt köteles a megbízóval egyeztetni az eltérést és az egyeztetés eredményét írásban is megküldeni a megbízó részére. \nA szeszesital árukban keletkezett károkra az önrészesedés mértéke 20%, de minimum 100 000 Ft"
        additional_txt_6 = "Amennyiben a rakodás írásbeli megállapodás alapján a biztosított felelősségére történt a biztosítás fedezete kiterjed az áru fel-, és lerakása során keletkezett károkra, bele nem értve azokat a káreseményeket, melyek idegen tulajdonú rakodóeszközzel a feladó, illetve az átvevő raktárában történtek, valamint bele nem értve az önrakodós teherautóval (KCR daru) végzett rakodásokat.\nRakodás során keletkezett károkra az önrészesedés mértéke: a keletkezett kár 20%-a, de minimum 200 000 Ft"

        # A CMR és BÁF feltételek összegyűjtve az összes csoportból
        cmr_clauses = []
        baf_clauses = []

        # placeholderekhez tartozó adatok
        transported_good = {}
        excluded_good = {}
        territorial_scope = {}
        numbers_of_truck = {}
        fee_per_truck = {}

        limit = []
        cmr_limits = {}
        baf_limits = {}

        additional_text = []
        cabotage = ""

        for group in self.groups:
            transported_goods = []
            excluded_goods = [", mobiltelefon", ", elektronikai áruk", ", jövedéki termék"]
            cabotage = group.cabotage if not cabotage else ""

            for i in range(len(group.cmr_clauses)):
                clause = group.cmr_clauses[i]
                if clause[2]:
                    if clause[0] not in cmr_clauses:
                        cmr_clauses.append(clause[0])
                    if i == 0 and additional_txt_1 not in additional_text:
                        additional_text.append(additional_txt_1)
                    elif i == 2 and sublimit_txt_1 not in limit:
                        limit.append(sublimit_txt_1)
                    elif i == 3 and sublimit_txt_2 not in limit:
                        limit.append(sublimit_txt_2)
                    elif i == 5:
                        if additional_txt_2 not in additional_text:
                            additional_text.append(additional_txt_2)
                        if ", jövedéki termék" in excluded_goods:
                            excluded_goods.remove(", jövedéki termék")
                    elif i == 8 and ", jövedéki termék" in excluded_goods:
                        excluded_goods.remove(", jövedéki termék")
                    elif i == 6 and ", elektronikai áruk" in excluded_goods:
                        excluded_goods.remove(", elektronikai áruk")
                    elif i == 9:
                        if ", mobiltelefon" in excluded_goods:
                            excluded_goods.remove(", mobiltelefon")
                        if additional_txt_4 not in additional_text:
                            additional_text.append(additional_txt_4)
                    if clause[3] not in transported_goods:
                        transported_goods.append(clause[3])

            for i in range(len(group.baf_clauses)):
                clause = group.baf_clauses[i]
                if clause[2]:
                    if clause[0] not in baf_clauses:
                        baf_clauses.append(clause[0])
                    if i == 0 and additional_txt_1 not in additional_text:
                        additional_text.append(additional_txt_1)
                    elif i == 2 and sublimit_txt_1 not in limit:
                        limit.append(sublimit_txt_1)
                    elif i == 3 and sublimit_txt_2 not in limit:
                        limit.append(sublimit_txt_2)
                    elif i == 5:
                        if ", jövedéki termék" in excluded_goods:
                            excluded_goods.remove(", jövedéki termék")
                        if additional_txt_2 not in additional_text:
                            additional_text.append(additional_txt_2)
                    elif i == 6 and additional_txt_3 not in additional_text:
                        additional_text.append(additional_txt_3)
                    elif i == 7 and ", elektronikai áruk" in excluded_goods:
                        excluded_goods.remove(", elektronikai áruk")
                    elif i == 9:
                        if ", jövedéki termék" in excluded_goods:
                            excluded_goods.remove(", jövedéki termék")
                        if additional_txt_5 not in additional_text:
                            additional_text.append(additional_txt_5)
                    elif i == 10 and additional_txt_6 not in additional_text:
                        additional_text.append(additional_txt_6)

                    if clause[3] not in transported_goods:
                        transported_goods.append(clause[3])

            new_eg = "CMR biztosítási feltételekben és a Belföldi közúti árutovábbítási felelősségbiztosítás <BÁF> feltételekben" if cmr_limits and baf_limits else "" \
                     "CMR biztosítási feltételekben" if cmr_limits else "Belföldi közúti árutovábbítási felelősségbiztosítás <BÁF> feltételekben"
            new_eg += " foglaltakon túl: költözési ingóság"

            new_tg = "normál kereskedelmi áru (csomagolt egységrakomány)"
            for good in transported_goods:
                new_tg += good

            for exclude in excluded_goods:
                new_eg += exclude

            new_ts = "földrajzi értelemben vett Európa, beleértve Magyarország, kizárva: Ukrajna, FÁK országok, Koszovó, Albánia" if group.cmr and group.baf else "földrajzi értelemben vett Európa, kizárva: Ukrajna, FÁK országok, Koszovó, Albánia" if group.cmr else "Magyarország"

            add_to_dict(transported_good, group.group_number[0], new_tg)
            add_to_dict(territorial_scope, group.group_number[0], new_ts)
            add_to_dict(excluded_good, group.group_number[0], new_eg)
            add_to_dict(numbers_of_truck, group.group_number[0], f"{group.number_of_trucks} db jármű", True)
            fpt = f"{format_string(group.fee_per_truck)},- Ft / szerelvény / év"
            add_to_dict(fee_per_truck, group.group_number[0], fpt, True)
            if group.cmr:
                add_to_dict(cmr_limits, group.group_number[0], group.cmr_limit)
            if group.baf:
                add_to_dict(baf_limits, group.group_number[0], group.baf_limit)

        limit1, limit2 = get_limits(limit, cmr_limits, baf_limits)

        additional_txt = ""
        for element in additional_text:
            if additional_txt:
                additional_txt += "\n"
            additional_txt += element

        return get_string(transported_good), get_string(excluded_good), get_string(territorial_scope), \
            get_string(numbers_of_truck), get_string(fee_per_truck), limit1, limit2, \
            list_to_string(cmr_clauses), list_to_string(baf_clauses), additional_txt, cabotage


class Group:
    def __init__(self):
        self.number_of_trucks = None
        self.cabotage = ""
        self.group_number = None

        self.cmr = False
        self.baf = False
        self.cmr_limit: int = 0
        self.baf_limit: int = 0

        self.fee_per_truck = None

        self.business_policy_discount = 0.8
        self.deductibles_discount = 0.9

        self.cmr_clauses = [
            ["CMRZ-834 Nyitott, fedetlen gépjárművel szállított áruk záradék", 1, False, ""],
            ["CMRZ-835 Ömlesztett áruk záradék ", 1, False, ", csomagolást nem igénylő ömlesztett áru"],
            ["CMRZ-836 Tartálykocsikkal szállított áruk záradék  ", 1.2, False, ""],
            ["CMRZ-837 Konténerek kárai záradék", 1.25, False, ""],
            ["CMRZ-838 Ásványolaj áruk záradék", 1.25, False, ", ásványolaj áruk"],
            ["CMRZ-839 Dohánytermék záradék", 1.25, False, ", dohánytermék"],
            ["CMRZ-840 Elektronikai áruk záradék", 1.1, False, ", elektronikai áruk"],
            ["CMRZ-841 Szabályozott hőmérsékleten szállítandó áruk záradék", 1.15, False, ", Szabályozott hőmérsékleten szállítandó áruk"],
            ["CMRZ-842 Szeszesital záradék", 1.15, False, ", szeszesital"],
            ["CMRZ-843 Mobiltelefon záradék", 1.15, False, ", mobiltelefon"],         # szöveg oldal alján
        ]
        self.baf_clauses = [
            ["B01.sz. záradék – Nyitott szállítóeszköz", 1, False, ""],
            ["B02.sz. záradék – Ömlesztett áruk kárai", 1, False, ", csomagolást nem igénylő ömlesztett áru"],
            ["B03.sz. záradék – Tartálykocsi", 1.2, False, ""],
            ["B04.sz. záradék – Konténeres áruszállítások kárai", 1.25, False, ""],
            ["B05.sz. záradék – Ásványolaj áruk kárai", 1.25, False, ", ásványolaj áruk"],
            ["B06.sz. záradék – Dohánytermékek kárai", 1.25, False, ", dohánytermék"],
            ["B07.sz. záradék – Kávéféleségek, édesség kárai", 1.25, False, ", Kávéféleségek, édesség"],
            ["B08.sz. záradék – Elektronikai áruk kárai", 1.2, False, ", elektronikai áruk"],
            ["B09.sz. záradék – Szabályozott hőmérsékleten szállítandó áruk kárai", 1.2, False, ", Szabályozott hőmérsékleten szállítandó áruk"],
            ["B10.sz. záradék – Szeszesital áruk kárai", 1.2, False, ", szeszesital"],
            ["B13.sz. záradék", 1.5, False, ""],                                # szöveg oldal alján
        ]

    def calculator(self):
        def calculator_cmr():
            if self.cmr_limit <= 50_000:
                fee = 69_996
            elif self.cmr_limit <= 100_000:
                fee = 84_996
            elif self.cmr_limit <= 200_000:
                fee = 102_996
            elif self.cmr_limit <= 300_000:
                fee = 129_996
            else:
                fee = self.cmr_limit * (129_996 / 300_000)

            # az aktív záradékok pótdíját hozzáadjuk a díjhoz
            for claus in self.cmr_clauses:
                if claus[2]:
                    fee *= claus[1]

            if self.cabotage:
                fee *= 1.2

            return fee

        def calculator_baf():
            if self.baf_limit <= 2_000_000:
                fee = 17_000
            elif self.baf_limit <= 4_000_000:
                fee = 27_000
            elif self.baf_limit <= 6_000_000:
                fee = 37_000
            elif self.baf_limit <= 8_000_000:
                fee = 48_000
            elif self.baf_limit <= 10_000_000:
                fee = 59_000
            elif self.baf_limit <= 15_000_000:
                fee = 85_000
            elif self.baf_limit >= 20_000_000:
                fee = 111_000
            else:
                fee = self.baf_limit * (111_000 / 20_000_000)

            # az aktív záradékok pótdíját hozzáadjuk a díjhoz
            for claus in self.baf_clauses:
                if claus[2]:
                    fee *= claus[1]
            return fee

        def discount():
            # autók száma kedvezmény:
            if self.number_of_trucks > 50:
                self.fee_per_truck *= 0.8
            elif self.number_of_trucks > 20:
                self.fee_per_truck *= 0.85
            elif self.number_of_trucks > 10:
                self.fee_per_truck *= 0.9
            elif self.number_of_trucks > 5:
                self.fee_per_truck *= 0.95

            # üzletpolitikai kedvezmény
            self.fee_per_truck *= self.business_policy_discount
            # önrész kedvezmény
            self.fee_per_truck *= self.deductibles_discount

        def cmr_minimum():
            if self.cmr_limit <= 50_000:
                if self.fee_per_truck < 60000:
                    self.fee_per_truck = 60000
            elif self.cmr_limit <= 100_000:
                if self.fee_per_truck < 75000:
                    self.fee_per_truck = 75000
            elif self.cmr_limit <= 200_000:
                if self.fee_per_truck < 93000:
                    self.fee_per_truck = 93000
            elif self.cmr_limit <= 300_000:
                if self.fee_per_truck < 110000:
                    self.fee_per_truck = 110000

        # CMR és BÁF
        if self.baf and self.cmr:
            self.fee_per_truck = calculator_cmr() + (0.5 * calculator_baf())
            discount()

        # csak CMR
        elif self.cmr_limit:
            self.fee_per_truck = calculator_cmr()
            discount()
            cmr_minimum()

        # csak BÁF
        else:
            self.fee_per_truck = calculator_baf()
            discount()

        self.fee_per_truck = int(self.fee_per_truck)
