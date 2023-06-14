import urllib

from flask import Flask, render_template, request, session, url_for, redirect
import hashlib, random
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = '123456789'
host = 'http://127.0.0.1:5000/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/checkSell', methods=['GET', 'POST'])
def checkSell():    # Checks if the user is also a seller or not
    conn = sql.connect('database.db')
    conn.commit()
    cursor = conn.cursor()
    email = session['name']

    query = "SELECT * FROM Sellers WHERE email='{}'"
    cursor.execute(query.format(email))
    result = cursor.fetchall()

    if result == []:   # Fetched data will be an empty list if the user is not a seller
        return render_template('failedSeller.html')
    else:
        return sellersHome()


@app.route('/checkBid', methods=['GET', 'POST'])
def checkBid():     # Checks if the user is also a bidder or not
    conn = sql.connect('database.db')
    conn.commit()
    cursor = conn.cursor()
    email = session['name']

    query = "SELECT * FROM Bidders WHERE email='{}'"
    cursor.execute(query.format(email))
    result = cursor.fetchall()

    if result == []:   # Fetched data will be an empty list if the user is not a bidder
        return render_template('failedBidder.html')
    else:
        return biddersHome()


@app.route('/myBids', methods=['GET', 'POST'])
def myBids():    # Function for retrieving and displaying the bids made by the user
    conn = sql.connect('database.db')
    conn.commit()
    cursor = conn.cursor()
    email = session['name']  # Had to join the bids and auction listings tables
    query = "SELECT Bids.Bid_ID, Bids.Seller_Email, Bids.Bid_price, Auction_Listings.Product_Name, Auction_Listings.Status, Auction_Listings.Max_Bids FROM Bids INNER JOIN Auction_Listings ON Bids.Listing_ID=Auction_Listings.Listing_ID WHERE Bids.Bidder_email='{}'"
    cursor.execute(query.format(email))
    result = cursor.fetchall()

    return render_template('myBids.html', result=result)


@app.route('/item/<data>', methods=['GET', 'POST'])
def item(data):
    if request.method=='GET':
        print("ENTERED ITEM")
        conn = sql.connect('database.db')
        conn.commit()
        cursor = conn.cursor()
        decoded_data = urllib.parse.unquote(data)
        query = "SELECT * FROM Auction_Listings WHERE Listing_ID='{}' AND Status=1"
        cursor.execute(query.format(decoded_data))
# Print statements useful for debugging
        print("List check")
        result = [*set(cursor.fetchall())]  # removes the tuples
        result = list(result[0])               # and turns it into a list form
        print(result)

        print(decoded_data)
        return render_template('item.html', result=result)


@app.route('/categories', methods=['GET', 'POST'])
def categories():
    conn = sql.connect('database.db')
    conn.commit()
    cursor = conn.cursor()

    if request.method == 'POST':  # when it detects a post request
        if request.form['submit-button'] == 'expand':
            print("IF STATEMENT")
            subcategories = request.form['button_name']
            print(subcategories)
            query = "SELECT category_name FROM Categories WHERE parent_category='{}'"
            cursor.execute(query.format(subcategories))
            result = [*set(cursor.fetchall())]
            result = [res[0] for res in result]
            print("result1: ", result)
            print("DONE IF STATEMENT")
            return render_template('categories.html', result=result)
        elif request.form['submit-button'] == 'lists':  # if-else statement checks which button is making the post request
            print("ELIF STATEMENT")
            category = request.form['button_name']
            query = "SELECT * FROM Auction_Listings WHERE Category='{}' AND Status=1"
            cursor.execute(query.format(category))
            print(category)
            result = cursor.fetchall()
            print("result2: ", result)
            return render_template('displayLists.html', result=result)
    else: #This is what is rendered by default when there is not post request
        print("ELSE statement")
        query = "SELECT category_name FROM Categories WHERE parent_category='Root'"
        cursor.execute(query)
        result = [*set(cursor.fetchall())]
        result = [res[0] for res in result]

        print(result)
        print(request.form)

        return render_template('categories.html', result=result)

@app.route('/update_bidder_account', methods=['GET', 'POST'])
def update_bidder_account():
    conn = sql.connect('database.db')
    conn.commit()
    cursor = conn.cursor()

    if request.method == 'POST':
        firstName=request.form['FirstName']  # Saving the information from the form to the variables
        lastName = request.form['LastName']
        gender = request.form['Gender']
        age = request.form['Age']
        major = request.form['Major']
        email = session['name']
        print(firstName) # Checking the variables by printing them
        print(email)
        print(lastName)

        # Updating the bidders information with what was submitted
        query = "UPDATE Bidders SET first_name='{}', last_name='{}', gender='{}', age='{}', major='{}' WHERE email='{}'"
        cursor.execute(query.format(firstName, lastName, gender, age, major, email))

        conn.commit()

        return bidder_account()

    query = "SELECT first_name, last_name, gender, age, major FROM Bidders where email='{}'"
    cursor.execute(query.format(session['name']))
    result = [*set(cursor.fetchall())]
    result = list(result[0])
    print(result)
    return render_template('update_bidder_account.html', biddersTable=result)


@app.route('/bidder_account', methods=['GET', 'POST'])
def bidder_account():
    print("Account class")

    conn = sql.connect('database.db')
    conn.commit()
    cursor = conn.cursor()

    email = session['name']

    query = "SELECT first_name, last_name, gender, age, major FROM Bidders where email='{}'"
    cursor.execute(query.format(session['name']))
    biddersTable = list(cursor.fetchall()[0])

    addressQuery = "SELECT Address.zipcode, Address.street_num, Address.street_name FROM Address JOIN Bidders ON Bidders.home_address_id = Address.address_ID WHERE Bidders.email='{}';"
    cursor.execute(addressQuery.format(email))
    addressContent = list(cursor.fetchall()[0])


    creditCardQuery = "SELECT Credit_Cards.credit_card_num, Credit_Cards.card_type, Credit_Cards.expire_month, Credit_Cards.expire_year, Credit_Cards.security_code FROM Bidders JOIN Credit_Cards ON Bidders.email = Credit_Cards.owner_email WHERE Bidders.email='{}';"
    cursor.execute(creditCardQuery.format(session['name']))
    cardContent = list(cursor.fetchall()[0])

    print(biddersTable)
    print(addressContent)
    print(cardContent)

    return render_template('bidder_account.html', biddersTable=biddersTable, addressContent=addressContent, cardContent=cardContent)

def getID(): # Used to generate a unique ID for a a product when being listed for the first time
    ID = random.randint(100, 3000)
    print("function call successful")
    return ID

@app.route('/updateVendorAccount', methods=['GET', 'POST'])
def updateVendorAccount():
    print("Update Vendor account")
    conn = sql.connect('database.db')
    conn.commit()
    cursor = conn.cursor()
    email = session['name']
    query = "SELECT Local_Vendors.Business_Name, Address.street_num, Address.street_name, Address.zipcode, Sellers.bank_routing_number, Sellers.bank_account_number, Sellers.balance, Local_Vendors.Customer_Service_Phone_Number FROM Sellers JOIN Local_Vendors ON Sellers.email = Local_Vendors.email JOIN Address ON Local_Vendors.Business_Address_ID = Address.address_ID WHERE Sellers.email='{}'"

    cursor.execute(query.format(email))
    result = [*set(cursor.fetchall())]
    result = list(result[0])
    print(result)

    if request.method == 'POST':
        print("update POST Sellers account")
        bankRoutingNumber = request.form['bankRoutingNumber']
        bankAccountNumber = request.form['bankAccountNumber']

        email = session['name']
        print(bankRoutingNumber)
        print(bankAccountNumber)
        print(email)
        query = "UPDATE Sellers SET bank_routing_number='{}', bank_account_number='{}' WHERE email='{}'"
        cursor.execute(query.format(bankRoutingNumber, bankAccountNumber, email))
        conn.commit()

        return sellersAccount()

    return render_template('updateVendorAccount.html', result=result)


@app.route('/updateSellersAccount', methods=['GET', 'POST'])
def updateSellersAccount(): # Function for updating the sellers account information
    print("Update Sellers account")
    conn = sql.connect('database.db')
    conn.commit()
    cursor = conn.cursor()
    email = session['name']

    query = "SELECT bank_routing_number, bank_account_number FROM Sellers WHERE email='{}'"
    cursor.execute(query.format(email))
    result = [*set(cursor.fetchall())]
    result = list(result[0])
    print(result)

    if request.method == 'POST':
        print("update POST Sellers account")
        bankRoutingNumber = request.form['bankRoutingNumber']
        bankAccountNumber = request.form['bankAccountNumber']

        businessName = request.form['businessName']
        streetNumber = request.form['streetNumber']
        streetName = request.form['streetName']
        zipcode = request.form['zipcode']
        customerServiceNumber = request.form['customerServiceNumber']

        email = session['name']
        print(bankRoutingNumber)
        print(bankAccountNumber)
        print(email)
                            # Three different queries for querying to three different tables
        sellersQuery = "UPDATE Sellers SET bank_routing_number='{}', bank_account_number='{}' WHERE email='{}'"
        cursor.execute(sellersQuery.format(bankRoutingNumber, bankAccountNumber, email))

        vendorQuery = "UPDATE Local_Vendors SET Business_Name='{}', Customer_Service_Phone_Number='{}' WHERE email='{}'"
        cursor.execute(vendorQuery.format(businessName, customerServiceNumber, email))

        addressQuery = "SELECT Business_Address_ID FROM Local_Vendors WHERE email='{}'"
        cursor.execute(addressQuery.format(email))
        getAddressID = cursor.fetchall()

        getAddressID = list(getAddressID[0])  # getting the address id

        updateAddress = "UPDATE Address SET zipcode='{}', street_num='{}', street_name='{}' WHERE address_ID='{}'"
        cursor.execute(updateAddress.format(zipcode, streetNumber, streetName, getAddressID[0]))

        conn.commit()  # committing the connection

        return sellersAccount()

    return render_template('updateSellersAccount.html', result=result)


@app.route('/sellersAccount', methods=['GET', 'POST'])
def sellersAccount():
    print("Sellers account")
    conn = sql.connect('database.db')
    conn.commit()
    cursor = conn.cursor()
# Vendors are also sellers. We need to check if the seller user is a vendor or not.
    # This is important when it comes to displaying their account information
       # as they have different informarions to be displayed
    vendorCheck = "SELECT * FROM Local_Vendors WHERE email='{}'" # Checks if the seller is alsoo a vendor or not
    cursor.execute(vendorCheck.format(session['name']))
    vendorResult = [*set(cursor.fetchall())]
    print(vendorResult)
    #vendorResult = list(vendorResult[0])

    if vendorResult == []: # [] indicates the seller is not a vendor
        query = "SELECT bank_routing_number, bank_account_number, balance FROM Sellers WHERE email='{}'"
        cursor.execute(query.format(session['name']))
        print(session['name'])   # print statements for debugging
        result = cursor.fetchall()
        print(result)
        result = [element for tup in result for element in tup]  # removing the tuples in a python list
        print(result)
        return render_template('sellersAccount.html', result=result)
    else:
        print("JOIN STATEMENT")
        email = session['name']
        print(email)
        query = "SELECT Local_Vendors.Business_Name, Address.street_num, Address.street_name, Address.zipcode, Sellers.bank_routing_number, Sellers.bank_account_number, Sellers.balance, Local_Vendors.Customer_Service_Phone_Number FROM Sellers JOIN Local_Vendors ON Sellers.email = Local_Vendors.email JOIN Address ON Local_Vendors.Business_Address_ID = Address.address_ID WHERE Sellers.email='{}'"
        cursor.execute(query.format(email))
        result = [*set(cursor.fetchall())]
        result = list(result[0])
        print(result)
        return render_template('vendorAccount.html', result=result)

@app.route('/sellers_myListings', methods=['GET', 'POST'])
def sellers_myListings():
    print("Sellers my listings")
    conn = sql.connect('database.db')
    conn.commit()
    cursor = conn.cursor()
    email = session['name']

    # Grouping the auction listings according to their statuses.
    # Listings that have statuses of 2 means they are sold, hence they cannot be edited
    query0 = "SELECT * FROM Auction_Listings WHERE Seller_Email='{}' AND Status=0"
    cursor.execute(query0.format(email))
    status0 = cursor.fetchall()

    query1 = "SELECT * FROM Auction_Listings WHERE Seller_Email='{}' AND Status=1"
    cursor.execute(query1.format(email))
    status1 = cursor.fetchall()


    query2 = "SELECT * FROM Auction_Listings WHERE Seller_Email='{}' AND Status=2"
    cursor.execute(query2.format(email))
    status2 = cursor.fetchall()

    return render_template('sellers_myListings.html', status0=status0, status1=status1, status2=status2)

@app.route('/deleteListing', methods=['GET', 'POST'])
def deleteListing():
    conn = sql.connect('database.db')
    conn.commit()
    cursor = conn.cursor()
# Function for deleting the auction listings
    ID = request.form['ID']
    reason = request.form['reason']
    print(ID)
    auctionQuery = "SELECT * FROM Auction_Listings WHERE Listing_ID='{}'"
    cursor.execute(auctionQuery.format(ID))
    result = cursor.fetchall()
    result = list(result[0])
    print(result)

    query = "DELETE FROM Auction_Listings WHERE Listing_ID='{}'"
    cursor.execute(query.format(ID))

    conn.execute("INSERT INTO Records (Seller_Email, Listing_ID, Category, Auction_Title, Product_Name, Product_Description, Quantity, Reserve_Price, Max_Bids, Status, Reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (result[0], ID, result[2], result[3], result[4], result[5], result[6], result[7], result[8], 1, reason))
    conn.commit()

    return redirect(url_for('sellers_myListings'))

@app.route('/process', methods=['GET', 'POST'])
def process():
    print("process")
    conn = sql.connect('database.db')
    conn.commit()
    cursor = conn.cursor()
    id = request.form['ID']
    session['ID'] = id

    queryCat = "SELECT category_name FROM Categories"
    cursor.execute(queryCat)
    categories = [*set(cursor.fetchall())]
    categories = [cat[0] for cat in categories]
    print(categories)

    query = "SELECT * FROM Auction_Listings WHERE Listing_ID='{}'"
    cursor.execute(query.format(id))
    result = list(cursor.fetchall()[0])
    print(result)

    return render_template('editListing.html', result=result, categories=categories)


@app.route('/editListing', methods=['GET', 'POST'])
def editListing(): # Function for modifying the listings
    if request.method == 'POST':
        print("post statement")
        conn = sql.connect('database.db')
        conn.commit()
        cursor = conn.cursor()

        id = session['ID']

        auctionTitle = request.form['AuctionTitle']
        productName = request.form['ProductName']
        category = request.form['Category']
        quantity = request.form['Quantity']
        reservePrice = request.form['ReservePrice']
        maxBids = request.form['MaxBids']
        productDescription = request.form['ProductDescription']

        query = "UPDATE Auction_Listings SET Auction_Title='{}', Product_Name='{}', Category='{}', Quantity='{}', Reserve_Price='{}', Max_bids='{}', Product_Description='{}' WHERE Listing_ID='{}'"
        cursor.execute(query.format(auctionTitle, productName, category, quantity, reservePrice, maxBids, productDescription, id))
        conn.commit()
        print("success")
        return redirect(url_for('sellers_myListings'))



@app.route('/sellersHome', methods=['GET', 'POST'])
def sellersHome():
    return render_template('sellersHome.html')

@app.route('/sellersListing', methods=['GET', 'POST'])
def sellersListing():
    conn = sql.connect('database.db')
    conn.commit()
    cursor = conn.cursor()

    query = "SELECT category_name FROM Categories" # Querying the categories
    cursor.execute(query)
    result = [*set(cursor.fetchall())]
    result = [res[0] for res in result]
    print(result)

    if request.method == 'POST':
        print("here")

        auctionTitle = request.form['AuctionTitle'] # Data from forms in variables
        productName = request.form['ProductName']
        category = request.form['Category']
        quantity = request.form['Quantity']
        reservePrice = request.form['ReservePrice']
        maxBids = request.form['MaxBids']
        productDescription = request.form['ProductDescription']

        ID = getID()

        queryID = "SELECT Listing_ID FROM Auction_Listings"
        cursor.execute(queryID)
        idList = [*set(cursor.fetchall())]
        idList = [int(id[0]) for id in idList]

        while ID in idList:
            ID = getID()

        conn.execute("INSERT INTO Auction_Listings (Seller_Email, Listing_ID, Category, Auction_Title, Product_Name, Product_Description, Quantity, Reserve_Price, Max_Bids, Status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (session['name'], ID, category, auctionTitle, productName, productDescription, quantity, reservePrice, maxBids, 1))

        conn.commit()
        conn.close()
        print("Data inserted")

        return redirect(url_for('sellers_myListings'))

    return render_template('sellersListing.html', result=result)

@app.route('/failed')
def failed(): # Failed login page
    return render_template('failed.html')

@app.route('/biddersHome')
def biddersHome(): # Bidders homepage
    return render_template('bidder.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        conn = sql.connect('database.db')
        conn.commit()
        cursor = conn.cursor()

        name = request.form['Username']
        password = request.form['Password']

        query = "SELECT * FROM Users where email='{}'"
        cursor.execute(query.format(name))
        result = cursor.fetchall()
        print(result)

        if result == []:
            return render_template('failed.html')
        else:
            hashedPwd = result[0][1]
            inputPwd = hashlib.sha256(password.encode('utf-8')).hexdigest()

            userType = request.form['userType']
            if inputPwd == hashedPwd:
                query = "SELECT * FROM {} where email='{}'"
                cursor.execute(query.format(userType, name))
                result = cursor.fetchall()

                if result == []:
                    return render_template('failed.html')
                else:
                    session['name'] = name
                    session['password'] = password
                    print(name)
                    if userType == 'Bidders':
                        return redirect(url_for('biddersHome'))
                    elif userType == 'Sellers':
                        return redirect(url_for('sellersHome'))
                    elif userType == 'HelpDesk':
                        return render_template('helpdesk.html')
            else:
                return render_template('failed.html')

    return render_template('input.html')


if __name__ == "__main__":
    app.run()


