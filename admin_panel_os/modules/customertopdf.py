import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

D_PATH = os.environ.get('D_PATH')
NEW_PATH = os.environ.get('NEW_PATH')

class CreateDOC:
    def __init__(self, customer):
        self.customer = customer
        self.doc = None
        self.new_doc_path = D_PATH
        self.create_template()
        self.document_data()

        self.doc.save(self.new_doc_path+".docx")
        os.startfile(self.new_doc_path+".docx")


    def create_template(self):
        for group in self.customer.groups:
            if group.cmr:
                self.customer.cmr = True
            if group.baf:
                self.customer.baf = True
        if self.customer.cmr and self.customer.baf:
            self.new_doc_path = f"{NEW_PATH}/{self.customer.company_name}_CMR_BAF_Ajánlat_{self.customer.broker}"
            self.doc = docx.Document(f'{D_PATH}/doc_template/cmrbaf_t.docx')
        elif self.customer.cmr:
            self.new_doc_path = f"{NEW_PATH}/{self.customer.company_name}_CMR_Ajánlat_{self.customer.broker}"
            self.doc = docx.Document(f'{D_PATH}/doc_template/cmr_t.docx')
        else:
            self.new_doc_path = f"{NEW_PATH}/{self.customer.company_name}_BAF_Ajánlat_{self.customer.broker}"
            self.doc = docx.Document(f'{D_PATH}/doc_template/baf_t.docx')

    def document_data(self):
        # bekezdések végigjárása és helykitöltők cseréje
        tg, eg, ts, nbr_tr, fpt, limit1, limit2, cmr_cl, baf_cl, add_txt, cb = self.customer.get_data()  # szállított áruk, kizárt áruk, területi hatály, járművek száma, egy jármű díja, limit paragrafusok(2)
        for paragraph in self.doc.paragraphs:
            text = paragraph.text
            if '@company_data' in text:
                par = paragraph.insert_paragraph_before("")
                par.add_run(f"Szerződő/Biztosított: \t{self.customer.company_name}").bold = True
                paragraph.insert_paragraph_before(f"Székhely: \t{self.customer.address}")
                if self.customer.registration_number != "@":
                    paragraph.insert_paragraph_before(f"Cégjegyzékszám: \t{self.customer.registration_number}")
                paragraph.text = f"Adószám: \t{self.customer.tax_number}"
            elif '@transported_goods' in text:
                paragraph.text = ""
                paragraph.add_run('Fuvarozott áruk köre:\t').bold = True
                paragraph.add_run(tg)
            elif '@excluded_goods' in text:
                paragraph.text = ""
                paragraph.add_run("Kizárt áruk köre: \t").bold = True
                paragraph.add_run(eg)
            elif "@number_of_trucks" in text:
                paragraph.text = ""
                paragraph.add_run("Fuvareszközök száma: \t").bold = True
                paragraph.add_run(nbr_tr)
            elif "@territorial_scope" in text:
                paragraph.text = ""
                paragraph.add_run("Területi hatály: \t").bold = True
                paragraph.add_run(ts)
                if cb != "":
                    paragraph.add_run(f"\nA biztosítás fedezete kiterjed a {cb}ban végzett belföldi közúti árufuvarozások (kabotázs) felelősségi kockázataira a CMR biztosítási feltételek szerint")
            elif "@payment_frequency" in text:
                paragraph.text = ""
                paragraph.add_run("Díjfizetés módja és üteme: \t").bold = True
                if self.customer.payment_frequency == 2:
                    freq = "negyed éves"
                elif self.customer.payment_frequency == 1:
                    freq = "fél éves"
                else:
                    freq = "éves"
                paragraph.add_run(f"banki átutalás; {freq} díjfizetési gyakoriság")
            elif "@limit" in text:
                if limit2 != "":
                    new_par = paragraph.insert_paragraph_before()
                    new_par.add_run("Kombinált kártérítési limit: \t").bold = True
                    new_par.add_run(limit1)
                    if cb != "":
                        new_par.add_run("\nKivéve a német kabotázs fuvarokat, ahol a CMR Egyezményben foglaltaknak megfelelően a hiányzó, illetve sérült áru bruttó súlya szerint kilogrammonként max. 8,33 SDR de mindösszesen maximum:\nEUR 600 000 / káresemény / év")
                    paragraph.text = ""
                    paragraph.add_run("Sublimit: \t").bold = True
                    paragraph.add_run(limit2)
                else:
                    paragraph.text = ""
                    paragraph.add_run("Kártérítési limit: \t").bold = True
                    paragraph.add_run(limit1)
                    if cb != "":
                        paragraph.add_run("\nKivéve a német kabotázs fuvarokat, ahol a CMR Egyezményben foglaltaknak megfelelően a hiányzó, illetve sérült áru bruttó súlya szerint kilogrammonként max. 8,33 SDR de mindösszesen maximum:\nEUR 600 000 / káresemény / év")
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT

            elif "@fee_truck" in text:
                paragraph.text = ""
                paragraph.add_run(f"Biztosítási díj: \t{fpt}").bold = True
            elif "@all_fee" in text:
                full_price = 0
                for group in self.customer.groups:
                    full_price += group.fee_per_truck * group.number_of_trucks
                full_price = f"{'{:,}'.format(full_price).replace(',', ' ')},-Ft"

                paragraph.text = ""
                paragraph.add_run(f"Biztosítási díj: \t{full_price}").bold = True
            elif "@additional" in text:
                paragraph.text = add_txt
                paragraph.paragraph_format.first_line_indent = 0
                paragraph.paragraph_format.left_indent = 0
                new_par = paragraph.insert_paragraph_before()
                new_par.alignment = WD_ALIGN_PARAGRAPH.LEFT
                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                new_par.add_run("Csatolt dokumentumok:\t").bold = True
                cmr = False
                baf = False
                for group in self.customer.groups:
                    if group.cmr:
                        cmr = True
                    if group.baf:
                        baf = True
                if cmr:
                    new_par.add_run("Biztosítási termékismertetők (IPID)\nCMR biztosítási feltételek\n").bold = True
                    new_par.add_run("Ügyfél- és Adatkezelési tájékoztató, Hasznos tudnivalók\nÁltalános Kárbiztosítási Feltételek\n"
                                      "Nemzetközi Közúti Árufuvarozói Felelősségbiztosítás (CMRkf)\nKülönös Feltételek és Záradékok\n")
                    new_par.add_run(cmr_cl)
                if baf:
                    if cmr:
                        new_par.add_run("\n")
                    new_par.add_run("Belföldi közúti árutovábbítási felelősségbiztosítás <BÁF>\n").bold = True
                    new_par.add_run("Ügyfél-és Adatkezelési tájékoztató, Hasznos tudnivalók\nÁltalános Kárbiztosítási Feltételek\n"
                                      "Belföldi Közúti Árutovábbítási Felelősségbiztosítás Különös Feltételek és Záradékok\n")
                    new_par.add_run(baf_cl)
