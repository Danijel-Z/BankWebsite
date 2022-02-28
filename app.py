from datetime import date, datetime
from flask import Flask, redirect, render_template, request, url_for, flash
from flask_migrate import Migrate, upgrade
from sqlalchemy import desc, func
from form import TransferForm, Deposit_Withdrawal_Form
from model import db, seedData, Customer , Transaction, Account, User, user_manager
from flask_user import roles_required, roles_accepted, current_user
from customerSearchEngine import addDocuments, createIndex, client

app = Flask(__name__)
app.config.from_object('config.ConfigDebug')

db.app = app
db.init_app(app)

migrate = Migrate(app, db)

user_manager.app = app
user_manager.init_app(app,db,User) 





def calculateNewBalance(choice, amount, findAccount):
    newAmount = findAccount.Balance

    if choice == "Deposit":
        newAmount = findAccount.Balance + amount
    
    elif choice == "Withdraw":
        newAmount = findAccount.Balance - amount
    
    return newAmount


def calculateAge(birthDate: date) -> int:
    today = date.today()
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
 
    return age

def getOrder(sortColumn, sortOrder, page, searchWord):
    
    if sortColumn == "" or sortColumn == None:
        sortColumn = "Surname"

    if sortOrder == "" or sortOrder == None:
        sortOrder = "asc"
    
    Customers = Customer.query.filter(
            Customer.GivenName.like('%' + searchWord + '%') | 
            Customer.City.like('%' + searchWord + '%') |
            Customer.id.like(searchWord) )
   
    if sortColumn == "Name":
        if sortOrder == "desc":
            Customers = Customers.order_by(Customer.Surname.desc())
        else:
            Customers = Customers.order_by(Customer.Surname.asc())

    if sortColumn == "City":
        if sortOrder == "desc":
            Customers = Customers.order_by(Customer.City.desc())
        else:
            Customers = Customers.order_by(Customer.City.asc())

    if sortColumn == "Streetaddress":
        if sortOrder == "desc":
            Customers = Customers.order_by(Customer.Streetaddress.desc())
        else:
            Customers = Customers.order_by(Customer.Streetaddress.asc())
    
    if sortColumn == "Birthday":
        if sortOrder == "desc":
            Customers = Customers.order_by(Customer.Birthday.desc())
        else:
            Customers = Customers.order_by(Customer.Birthday.asc())
    
    if sortColumn == "Customer ID":
        if sortOrder == "desc":
            Customers = Customers.order_by(Customer.id.desc())
        else:
            Customers = Customers.order_by(Customer.id.asc())

    paginationObject = Customers.paginate(page,50,False)

    return paginationObject

# {% load static %}
# {% static 'style.css' %}


# @app.route("/login", methods=["POST", "GET"])
# #@roles_required("Admin") 
# #@roles_accepted("Admin", "Cashier") ## Här kan man vara antingen admin eller customer
# def login():
#     pass


@app.route("/k", methods= ["POST", "GET"])
def customersVG():
    
    sortColumn = request.args.get('sortColumn', "id")
    sortOrder = request.args.get('sortOrder', "asc")
    page = int(request.args.get('page', 1))

    search = request.args.get('search','')

    skip = (page-1) * 50
    result = client.search(search_text=search,
        include_total_count=True,skip=skip,
        top=50,
        order_by= sortColumn + ' '  + sortOrder )
    total_pages = round( result.get_count()/50 )
    if total_pages == 0:
        total_pages = 1
    top = 50
    alla = result
    return render_template('k.html', listOfCustomers=alla, page = page, sortColumn = sortColumn, sortOrder = sortOrder,
                                     search = search, skip=skip, top = top, pages = total_pages )



@app.route("/customerCard", methods=["POST", "GET"])
@roles_accepted("Admin", "Cashier")
def customerCard():
    customer_id = request.args.get('customer_id', "")

    foundedCustomer = Customer.query.get(customer_id)
    totalMoneyFromAccounts = 0
    customer_age = 0
    if foundedCustomer:
        totalMoneyFromAccounts = sum( [acc.Balance for acc in foundedCustomer.Accounts] )
        totalMoneyFromAccounts = "${:,}".format(totalMoneyFromAccounts)

        year, month, day = foundedCustomer.Birthday.strftime('%Y-%m-%d').split('-')
        customer_age = calculateAge( date( int(year), int(month), int(day) ) ) 

    return render_template('customerCard.html', customer_age= customer_age, foundedCustomer = foundedCustomer, customer_id= customer_id, totalMoneyFromAccounts= totalMoneyFromAccounts)




@app.route("/transfer", methods=["POST", "GET"])
@roles_required("Admin") 
def transfer():
    form = TransferForm()
    if form.validate_on_submit():

        fromAccount = Account.query.get(form.fromAccount.data)
        toAccount = Account.query.get(form.toAccount.data)
        amountToTransfer = form.amount.data

        if fromAccount != None and toAccount != None :

            newBalanceFromAccount = calculateNewBalance("Withdraw", amountToTransfer, fromAccount)
            newBalanceToAccount = calculateNewBalance("Deposit", amountToTransfer, toAccount)

            transactionFromAccount = Transaction("Debit", "Transfer", datetime.now(), amountToTransfer, newBalanceFromAccount, fromAccount.id)
            transactionToAccount = Transaction("Debit", "Transfer", datetime.now(), amountToTransfer, newBalanceToAccount, toAccount.id)

            fromAccount.Balance = newBalanceFromAccount
            toAccount.Balance = newBalanceToAccount

            db.session.add_all([transactionFromAccount, transactionToAccount])
            db.session.commit()

            flash("Your money transfer has been succesful.")
            return redirect('transfer')

        flash("Something went wrong, please contact the authors.")
        return redirect('transfer')
    
    return render_template('transfer.html', form = form )




@app.route("/deposit&withdraw", methods=["POST", "GET"])
@roles_required("Admin") 
def deposit_withdraw():
    form = Deposit_Withdrawal_Form()
    if form.validate_on_submit():
        
        findAccount = Account.query.filter(Account.id == form.fromAccount.data).first()

        if findAccount:
            choice = form.choice.data
            amount = form.amount.data
            
            newBalance = calculateNewBalance(choice, amount, findAccount)
        
            newAccountTransaction = Transaction("Debit", choice, datetime.now(), amount, newBalance, findAccount.id)

            findAccount.Balance = newBalance

            db.session.add(newAccountTransaction)
            db.session.commit()
            

            return redirect( url_for('deposit_withdraw', form = form) )
        
    return render_template('deposit_withdraw.html', form = form )








@app.route("/transaction/<int:account_id>", methods= ["GET", "POST"])
@roles_accepted("Admin", "Cashier")
def transaction(account_id):
    foundedTransaction = Transaction.query.filter(Transaction.AccountId == account_id)
    customer_id = request.args.get('customer_id')

    if foundedTransaction.first():
        accountTransactions = foundedTransaction.order_by(Transaction.Date.desc())
        page = int(request.args.get('page', 1))
        paginationObject = accountTransactions.paginate(page,20,False)
        accountBalance = foundedTransaction.first().Account.Balance
        accountBalance = "${:,}".format(accountBalance)
        #customer_id = foundedTransaction.Account.CustomerId ##  Ger Customer ID
        return render_template('transaction.html', account_id = account_id, accountBalance= accountBalance, customer_id= customer_id,  accountTransactions = paginationObject.items, has_next= paginationObject.has_next,
                                has_prev= paginationObject.has_prev, pages= paginationObject.pages , page = page)
    
    return redirect(url_for('customerCard', customer_id= customer_id ))


@app.route("/customers", methods= ["GET", "POST"])
def customers():
    sortColumn = request.args.get('sortColumn')
    sortOrder = request.args.get('sortOrder')
    page = int(request.args.get('page', 1))
    searchWord = request.args.get('search','')
    listOfCustomers= getOrder(sortColumn, sortOrder, page, searchWord)
    
    join= db.session.query(Customer, Account).join(Account).where(Customer.id == 1544).order_by(desc(Account.Balance)).all()

    transaktioner = Account.query.all()
   
    
    return render_template("customers.html",
    join = join,  
    listOfCustomers = listOfCustomers.items, 
    page=page,
    sortColumn=sortColumn,
    sortOrder=sortOrder,
    q=searchWord,
    has_next= listOfCustomers.has_next,
    has_prev= listOfCustomers.has_prev, 
    pages= listOfCustomers.pages,
    transaktioner = transaktioner)

@app.route("/")
def startpage():
    numberOfCustomers = Customer.query.count()
    numberOfAccounts =  Account.query.count()
    TotalAccountsMoney = db.session.query(func.sum(Account.Balance)).all()
    TotalAccountsMoney = "${:,}".format(TotalAccountsMoney[0][0])  
    
    return render_template("startpage.html", numberOfAccounts = numberOfAccounts, numberOfCustomers= numberOfCustomers, TotalAccountsMoney = TotalAccountsMoney)

@app.route("/tstartpage")
def teststartpage():
    endastBalance= db.session.query(Account.Balance).all()
    numberOfCustomers = Customer.query.count()
    numberOfAccounts =  Account.query.count()
    TotalAccountsMoney = db.session.query(func.sum(Account.Balance)).all()
    TotalAccountsMoney = TotalAccountsMoney[0][0]
    return render_template("index.html", numberOfAccounts = numberOfAccounts, numberOfCustomers= numberOfCustomers, TotalAccountsMoney = TotalAccountsMoney)

@app.route("/charts")
def charts():
    return render_template("pages/charts/chartjs.html")



################### UI ELements #####################
@app.route("/buttons")
def buttons():
    return render_template("pages/ui-features/buttons.html")

@app.route("/dropdowns")
def dropdowns():
    return render_template("pages/ui-features/dropdowns.html")

@app.route("/typography")
def typography():
    return render_template("pages/ui-features/typography.html")

@app.route("/icons")
def icons():
    return render_template("pages/icons/mdi.html")

################### End Of UI ELements #####################


if __name__ == "__main__":
    with app.app_context():
        upgrade()
        seedData()
    app.run(host="127.0.0.1", port=5000, debug=True)
    
