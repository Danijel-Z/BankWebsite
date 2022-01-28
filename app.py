from datetime import date, datetime
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from sqlalchemy import desc, func
from form import TransferForm, Deposit_Withdrawal_Form
from model import db, seedData, Customer , Transaction, Account, User, user_manager

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

    paginationObject = Customers.paginate(page,20,False)

    return paginationObject
# {% load static %}
# {% static 'style.css' %}

@app.route("/transfer", methods=["POST", "GET"])
def transfer():
    form = TransferForm()
    if form.validate_on_submit():
        return redirect('test.html')
    return render_template('pay_or_transfer.html', form = form )




@app.route("/deposit&withdraw", methods=["POST", "GET"])
def deposit_withdraw():
    form = Deposit_Withdrawal_Form()
    if form.validate_on_submit():
        findAccount = Account.query.filter(Account.id == form.fromAccount.data).first()
        findAccount = Account.query.get(form.fromAccount.data)

        if findAccount:
            choice = form.choice.data
            amount = form.amount.data
            
            newBalance = calculateNewBalance(choice, amount, findAccount)
        
            newAccountTransaction = Transaction()
        
            newAccountTransaction.Type = "Debit"
            newAccountTransaction.Operation = choice
            newAccountTransaction.Date = datetime.now()
            newAccountTransaction.Amount = amount
            newAccountTransaction.NewBalance = newBalance
            newAccountTransaction.AccountId = findAccount.id

            findAccount.Balance = newBalance

            db.session.add(newAccountTransaction)
            db.session.commit()

            return redirect( url_for('deposit_withdraw', form = form) )
        
    return render_template('deposit_withdraw.html', form = form )








@app.route("/transaction/<int:account_id>", methods= ["GET", "POST"])
def transaction(account_id):
    foundedTransaction = Transaction.query.filter(Transaction.AccountId == account_id)
    if foundedTransaction.first():
        accountTransactions = foundedTransaction.order_by(Transaction.Date.desc())
        page = int(request.args.get('page', 1))
        paginationObject = accountTransactions.paginate(page,20,False)
        customer_id = request.args.get('customer_id')
        accountBalance = foundedTransaction.first().Account.Balance
        accountBalance = "${:,}".format(accountBalance)
        #customer_id = foundedTransaction.Account.CustomerId ##  Ger Customer ID
        return render_template('transaction.html', account_id = account_id, accountBalance= accountBalance, customer_id= customer_id,  accountTransactions = paginationObject.items, has_next= paginationObject.has_next,
                                has_prev= paginationObject.has_prev, pages= paginationObject.pages , page = page)
    
    return redirect(url_for('test'))
    



@app.route("/test", methods= ["GET", "POST"])
def test():
    sortColumn = request.args.get('sortColumn')
    sortOrder = request.args.get('sortOrder')
    page = int(request.args.get('page', 1))
    searchWord = request.args.get('search','')
    listOfCustomers= getOrder(sortColumn, sortOrder, page, searchWord)

    customer_id = request.args.get('customer_id', "")

    foundedCustomer = Customer.query.get(customer_id)
    totalMoneyFromAccounts = 0
    customer_age = 0
    if foundedCustomer:
        totalMoneyFromAccounts = sum( [acc.Balance for acc in foundedCustomer.Accounts] )
        totalMoneyFromAccounts = "${:,}".format(totalMoneyFromAccounts)
        year, month, day = foundedCustomer.Birthday.strftime('%Y-%m-%d').split('-')
        customer_age = calculateAge(date(int(year), int(month), int(day))) 
    join= db.session.query(Customer, Account).join(Account).where(Customer.id == 1544).order_by(desc(Account.Balance)).all()
    # listOfCustomers = Customer.query.get(1544)
    # listOfCustomers = Customer.query.limit(5).all()
    allCustomers = Customer.query.count()
    test = Customer.query.filter(Customer.id == 1544).first()
    hej = Customer.query.limit(0.1*allCustomers+1).all()
    transaktioner = Account.query.all()
    #listOfCustomers = db.session.query(Account).filter_by(id == 1).first()
#.label('Money_Amount')
    
    return render_template("test.html", customer_age= customer_age, foundedCustomer = foundedCustomer, customer_id= customer_id, totalMoneyFromAccounts= totalMoneyFromAccounts,
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

@app.route("/tstartpage")
def teststartpage():
    # h = db.session.query(Customer)
    # d = h.order_by(desc(Customer.id)).all()
    numberOfCustomers = Customer.query.count()
    numberOfAccounts =  Account.query.count()
    TotalAccountsMoney = db.session.query(func.sum(Account.Balance)).all()
    TotalAccountsMoney = TotalAccountsMoney[0][0]
    return render_template("teststartpage.html", numberOfAccounts = numberOfAccounts, numberOfCustomers= numberOfCustomers, TotalAccountsMoney = TotalAccountsMoney)

@app.route("/")
def startpage():
    endastBalance= db.session.query(Account.Balance).all()
    numberOfCustomers = Customer.query.count()
    numberOfAccounts =  Account.query.count()
    TotalAccountsMoney = db.session.query(func.sum(Account.Balance)).all()
    TotalAccountsMoney = TotalAccountsMoney[0][0]
    #trendingCategories = Category.query.all()
    #trendingCategories=trendingCategories
    return render_template("index.html", numberOfAccounts = numberOfAccounts, numberOfCustomers= numberOfCustomers, TotalAccountsMoney = TotalAccountsMoney)

@app.route("/charts")
def charts():
    return render_template("pages/charts/chartjs.html")

@app.route("/forms")
def forms():
    return render_template("pages/forms/basic_elements.html")

@app.route("/tables")
def tables():
    return render_template("pages/tables/basic-table.html")

@app.route("/error404")
def error404():
    return render_template("pages/samples/error-404.html")

@app.route("/error500")
def error500():
    return render_template("pages/samples/error-500.html")

@app.route("/login")
def login():
    return render_template("pages/samples/login.html")

@app.route("/register")
def register():
    return render_template("pages/samples/register.html")


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


@app.route("/category/<id>")
def category(id):
    products = Product.query.all()
    return render_template("category.html", products=products)


if __name__ == "__main__":
    with app.app_context():
        upgrade()
        seedData(db)
    app.run(host="127.0.0.1", port=5000, debug=True)
    
