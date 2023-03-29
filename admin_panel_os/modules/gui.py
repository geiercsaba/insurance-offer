from tkinter import *
from tkinter import messagebox, font, filedialog
from modules.customer import Customer
from modules.customertopdf import CreateDOC
from modules.db import DB
import os


class GUI:
    def __init__(self):
        self.window = Tk()
        self.font_size = font.Font(size=18)
        self.window.title("Ajánlatkészítő")
        self.db = DB()

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
        def on_click():
            for i in range(len(groups_entrys)):
                entries = groups_entrys[0]
                for n in range(len(entries)):
                    group = customer.groups[i]
                    # number_of_trucks, cmr_limit, baf_limit, cabotage, fee_per_truck
                    if n == 0:
                        group.number_of_trucks = int(entries[n].get())
                    elif n == 1:
                        group.cmr_limit = int(entries[n].get())
                    elif n == 2:
                        group.baf_limit = int(entries[n].get())
                    elif n == 3:
                        group.cabotage = entries[n].get()
                    elif n == 4:
                        group.fee_per_truck = int(entries[n].get())
            folder_path = filedialog.askdirectory()
            CreateDOC(customer, folder_path)

            messagebox.showinfo("Info!", "Az ajánlat sikeresen elkészült!")
            print(customer.id)
            self.db.update_customer(customer.id)
        window = Toplevel()

        # Ügyfél adatok
        company_data = LabelFrame(window, text="Ügyfél adatok")
        company_data.grid(row=0, column=0)
        company_data.columnconfigure(0, minsize=400)
        Label(company_data, text=f"Szerződő: {customer.company_name}\nSzékhely: {customer.address}\n"
                   f"Cégjegyzékszám: {customer.registration_number}\nAdószám: {customer.tax_number}", font=self.font_size).grid(row=0, column=0)

        # Alkusz adatok
        broker = LabelFrame(window, text=f"Alkusz adatai")
        broker.grid(row=1, column=0)
        broker.columnconfigure(0, minsize=400)
        Label(broker, text=f"Akusz: {customer.broker}\ne-mail: {customer.email}", font=self.font_size).grid(row=0, column=0)

        # Csoport adatok
        groups_entrys = []
        for i in range(len(customer.groups)):
            entries = []    # number_of_trucks, cmr_limit, baf_limit, cabotage, fee_per_truck
            group = customer.groups[i]

            group_label = LabelFrame(window, text=group.group_number)
            group_label.columnconfigure(0, minsize=200)
            group_label.columnconfigure(1, minsize=200)
            group_label.grid(row=2+i, column=0)

            Label(group_label, text="Járművek száma: ").grid(row=0, column=0)
            entry = Entry(group_label, textvariable=StringVar(group_label, group.number_of_trucks))
            entry.grid(row=0, column=1)
            entries.append(entry)

            Label(group_label, text="CMR limit: ").grid(row=1, column=0)
            entry = Entry(group_label, textvariable=StringVar(group_label, group.cmr_limit))
            entry.grid(row=1, column=1)
            entries.append(entry)

            Label(group_label, text="BÁF limit: ").grid(row=2, column=0)
            entry = Entry(group_label, textvariable=StringVar(group_label, group.baf_limit))
            entry.grid(row=2, column=1)
            entries.append(entry)

            if group.cmr:
                cmr = ""
                for clause in group.cmr_clauses:
                    if clause[2] == True:
                        if cmr != "":
                            cmr += "\n"
                        cmr += f"{clause[0]}"
                if cmr == "":
                    cmr = "-"
                Label(group_label, text="CMR záradékok: ").grid(row=3, column=0)
                Label(group_label, text=cmr).grid(row=3, column=1)

            if group.baf:
                baf = ""
                for clause in group.baf_clauses:
                    if clause[2] == True:
                        if baf != "":
                            baf += "\n"
                        baf += f"{clause[0]}"
                if baf == "":
                    baf = "-"
                Label(group_label, text="BÁF záradékok: ").grid(row=4, column=0)
                Label(group_label, text=baf).grid(row=4, column=1)

            entry = Entry(group_label, textvariable=StringVar(group_label, group.cabotage))
            if group.cabotage != "":
                Label(group_label, text="Kabotázs fuvart végez: ").grid(row=5, column=0)
                entry.grid(row=5, colum=1)
            entries.append(entry)

            Label(group_label, text="Csoport díja: ").grid(row=6, column=0)
            entry = Entry(group_label, textvariable=StringVar(group_label, group.fee_per_truck))
            entry.grid(row=6, column=1)
            entries.append(entry)
            groups_entrys.append(entries)

        Button(group_label, text="Ajánlat elkészítése", command=on_click).grid(row=7, column=0)
        Button(group_label, text="Vissza", command=window.destroy).grid(row=7, column=1)




