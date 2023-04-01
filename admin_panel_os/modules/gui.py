from tkinter import *
from tkinter import messagebox, font, filedialog
from modules.customer import Customer
from modules.customertopdf import CreateDOC
from modules.db import DB
from modules.web_util import check_company


class GUI:
    def __init__(self):
        self.window = Tk()
        self.font_size = font.Font(size=18)
        self.window.title("Ajánlatkészítő")
        self.db = DB()
        self.open_tl = False

        self.customers = []
        self.customers_get()

        self.show_records()
        self.window.mainloop()

    def customers_get(self):
        customers = self.db.get_customers()
        for customer in customers:
            customer_id = customer["id"]
            groups = self.db.get_groups(customer_id)

            new_customer = Customer()
            new_customer.customer_form_json(customer, groups)
            self.customers.append(new_customer)

    def show_records(self):
        for i, customer in enumerate(self.customers):
            new_frame = LabelFrame(self.window, text=customer.company_name)
            new_frame.grid(row=i, column=0)
            Label(new_frame, text=f"Alkusz: {customer.broker}    Csoportok: {len(customer.groups)} db").grid(row=0, column=0)
            Button(new_frame, text="Ajánlat", command=lambda cust=customer: self.show_customer(cust)).grid(row=0, column=1)

    def show_customer(self, customer):
        if len(self.window.winfo_children()) > 1:
            messagebox.showinfo("Figyelem!", "Egyszerre csak egy ajánlatot készíthetsz")
            return
        def format_string(txt):
            return '{:,}'.format(txt).replace(',', ' ')

        def on_click():
            CreateDOC(customer)
            self.db.update_customer(customer.id)
            window.destroy()

        def check_customer():
            info, data = check_company(customer)

            message_box = messagebox.askquestion("Változás", info)
            if message_box == 'yes' and data:
                customer.company_name = data[0]
                customer.address = data[1]
                customer.registration_number = data[2]
                customer.tax_number = data[3]
                company_label.config(text=f"Szerződő: {customer.company_name}\n"
                                          f"Székhely: {customer.address}\n"
                                          f"Cégjegyzékszám: {customer.registration_number}\n"
                                          f"Adószám: {customer.tax_number}")
            else:
                pass

        window = Toplevel(self.window)

        # Ügyfél adatok
        company_data = LabelFrame(window, text="Ügyfél adatok")
        company_data.grid(row=0, column=0)
        company_data.columnconfigure(0, minsize=600)
        company_label = Label(company_data, text=f"Szerződő: {customer.company_name}\nSzékhely: {customer.address}\n"
              f"Cégjegyzékszám: {customer.registration_number}\nAdószám: {customer.tax_number}",
              font=self.font_size)
        company_label.grid(row=0, column=0, columnspan=2)
        Button(company_data, text="Ellenőrzés", command=check_customer).grid(row=1, column=0, columnspan=2)

        # Alkusz adatok
        broker = LabelFrame(window, text=f"Alkusz adatai")
        broker.grid(row=1, column=0)
        broker.columnconfigure(0, minsize=600)
        Label(broker, text=f"Akusz: {customer.broker}\ne-mail: {customer.email}", font=self.font_size).grid(row=0, column=0)

        # Csoport adatok
        for i in range(len(customer.groups)):
            group = customer.groups[i]

            group_label = LabelFrame(window, text=group.group_number)
            group_label.columnconfigure(0, minsize=200)
            group_label.columnconfigure(1, minsize=400)
            group_label.grid(row=2+i, column=0)

            Label(group_label, text="Járművek száma: ").grid(row=0, column=0)
            Label(group_label, text=f"{group.number_of_trucks} db").grid(row=0, column=1)

            Label(group_label, text="CMR limit: ").grid(row=1, column=0)
            Label(group_label, text=f"EUR {format_string(group.cmr_limit)}").grid(row=1, column=1)

            Label(group_label, text="BÁF limit: ").grid(row=2, column=0)
            Label(group_label, text=f"{format_string(group.baf_limit)},-Ft").grid(row=2, column=1)

            if group.cmr:
                cmr = ""
                for clause in group.cmr_clauses:
                    if clause[2]:
                        if cmr:
                            cmr += "\n"
                        cmr += f"{clause[0]}"
                if not cmr:
                    cmr = "-"
                Label(group_label, text="CMR záradékok: ").grid(row=3, column=0)
                Label(group_label, text=cmr).grid(row=3, column=1)

            if group.baf:
                baf = ""
                for clause in group.baf_clauses:
                    if clause[2]:
                        if baf:
                            baf += "\n"
                        baf += f"{clause[0]}"
                if not baf:
                    baf = "-"
                Label(group_label, text="BÁF záradékok: ").grid(row=4, column=0)
                Label(group_label, text=baf).grid(row=4, column=1)

            if group.cabotage:
                Label(group_label, text="Kabotázs fuvart végez: ").grid(row=5, column=0)
                Label(group_label, text=f"{group.cabotage}").grid(row=5, column=1)

        #Díjak
        def calculator():
            fee = 0
            for j in range(len(customer.groups)):
                gr = customer.groups[j]
                gr.fee_per_truck = int(entries[j].get())
                fee += (gr.fee_per_truck * gr.number_of_trucks)
            full_fee.config(text=f"{fee},-Ft")

        fee = LabelFrame(window, text=f"Díjak")
        fee.columnconfigure(0, minsize=300)
        fee.columnconfigure(1, minsize=300)
        fee.grid(row=3+i, column=0)
        entries = []
        for n in range(len(customer.groups)):
            group = customer.groups[n]
            Label(fee, text=group.group_number).grid(row=0+n, column=0)
            entry = Entry(fee)
            group.calculator()
            entry.insert(0, group.fee_per_truck)
            entry.grid(row=0+n, column=1)
            entries.append(entry)
        Button(fee, text="Számítás", command=calculator).grid(row=n+1, columnspan=2)

        Label(fee, text="Teljes díj: ").grid(row=n+2, column=0)
        full_fee = Label(fee)
        full_fee.grid(row=n+2, column=1)
        calculator()



        Button(window, text="Ajánlat elkészítése", command=on_click).grid(row=4+i, column=0)
