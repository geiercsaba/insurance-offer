class Customer:
    def __init__(self):
        self.company_name = None
        self.address = None
        self.tax_number = None
        self.registration_number = None
        self.payment_frequency = None

        self.broker = None
        self.email = None

        self.nbr_of_groups = 1
        self.groups = []


class Group:
    def __init__(self):
        self.number_of_trucks = None
        self.cabotage = ""
        self.group_number = None

        self.cmr = False
        self.cmr_limit: int = 0
        self.baf = False
        self.baf_limit: int = 0

        self.fee_per_truck = None

        self.business_policy_discount = 0.8
        self.deductibles_discount = 0.9

        self.cmr_clauses = [
            ["CMRZ-834 Nyitott, fedetlen gépjárművel szállított áruk záradék", 1, False, ""],
            ["CMRZ-835 Ömlesztett áruk záradék", 1, False, ", csomagolást nem igénylő ömlesztett áru"],
            ["CMRZ-836 Tartálykocsikkal szállított áruk záradék", 1.2, False, ""],
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
