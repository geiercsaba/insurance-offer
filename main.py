from flask import Flask, request, render_template, redirect, url_for
from modules.customer import Customer, Group
from modules.db import save_database
import pymysql.cursors

app = Flask(__name__)
group_n = 0
customer = Customer()



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        customer.company_name = request.form['company_name']
        customer.address = request.form["company_address"]
        customer.registration_number = request.form["registration_number"]
        if customer.registration_number == "":
            customer.registration_number = "@"
        customer.tax_number = request.form["company_tax"]
        customer.nbr_of_groups = request.form["group_numbers"]
        if customer.nbr_of_groups == "":
            customer.nbr_of_groups = 1
        else:
            customer.nbr_of_groups = int(customer.nbr_of_groups)
        customer.payment_frequency = int(request.form["payment_frequency"])
        customer.broker = request.form["broker"]
        customer.email = request.form["email"]
        return redirect(url_for('group_data'))
    return render_template("index.html")


@app.route('/group_data', methods=['GET', 'POST'])
def group_data():
    global group_n
    if request.method == 'POST':
        group = Group()
        group.group_number = f"{chr(ord('a') + group_n)}. csoport"

        cmr = request.form["cmr"]
        if cmr == "":
            group.cmr_limit = 0
            group.cmr = False
        else:
            group.cmr_limit = int(cmr)
            group.cmr = True
        baf = request.form["baf"]
        if baf == "":
            group.baf_limit = 0
            group.baf = False
        else:
            group.baf_limit = int(baf)
            group.baf = True

        group.number_of_trucks = int(request.form["number_of_trucks"])
        if "cabotage_add" in request.form:
            group.cabotage = request.form["cabotage_add"]


        if "cmr_clauses" in request.form:
            list = request.form.getlist('cmr_clauses')
            for i in range(len(group.cmr_clauses)):
                if str(i) in list:
                    group.cmr_clauses[i][2] = True
        if "baf_clauses" in request.form:
            list = request.form.getlist('baf_clauses')
            for i in range(len(group.baf_clauses)):
                if str(i) in list:
                    group.baf_clauses[i][2] = True

        customer.groups.append(group)
        group_n += 1
        if group_n >= customer.nbr_of_groups:
            group_n = 0
            return redirect(url_for('succes'))
    return render_template("group.html", group=f"{chr(ord('a')+group_n)}. csoport")

@app.route('/submit')
def succes():
    save_database(customer)
    return render_template("succes.html")


if __name__ == '__main__':
    app.run(debug=True)
