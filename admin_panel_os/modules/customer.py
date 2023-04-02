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
            ["CMRZ-843 Mobiltelefon záradék", 1.15, False, ", mobiltelefon"],
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
            ["B13.sz. záradék", 1.5, False, ""],
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
