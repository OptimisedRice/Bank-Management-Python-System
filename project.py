# CA2 OOP - Bank Management System
import datetime
import random
import os


# general account class which will act as a superclass/parent to different account types
class Account(object):
    """General superclass for an account. Used as a parent for subclasses defined
    as account types"""
    def __init__(self, acc_number, name, IBAN, funds, transactions="None"):
        """constructor to initialise the object. most attributes are protected so that only the class
        and its subclasses can access them"""
        self._acc_number = acc_number  # protected acc number for security reasons. only to be used for identification
        self._name = name # protected name to identify between the user's accounts
        self.IBAN = IBAN  # public IBAN to be used for money transfers
        self._funds = funds  # protected funds
        if transactions == "None":  # avoid problems with mutable lists. protected too for security reasons
            self._transactions = []
        else:
            transactions = transactions.strip().split(",")
            self._transactions = transactions

    def get_balance(self):
        """get method for retrieving the balance of an account"""
        return self._funds

    def get_acc(self):
        """get method for retrieving account number"""
        return self._acc_number

    def get_name(self):
        """get method for retrieving the name"""
        return self._name

    def get_transactionlist(self):
        """get method for formatting the account transaction list attribute into a string.
        This is to be used for writing/updating the accounts.txt file. Each element of the
        transactions list is appended to a string and separated by commas"""
        transactionlist = ''  # format the transaction list into a writeable string
        if not self._transactions:
            return "None"
        for t, l in enumerate(self._transactions):
            if t == (len(self._transactions) - 1):  # end of line to not append a comma
                transactionlist += str(self._transactions[t])
            else:
                transactionlist += str(self._transactions[t]) + ","  # separate each element(transaction id) with a comma
        return transactionlist

    def withdraw(self, amount):
        """withdraw method for taking out money. error checking is done first and then the transaction
        is recorded in the accountsTransactions.txt file. Funds are then removed from the account"""
        if int(amount) <= 0:
            print("You can only withdraw a positive value")  # error validation for negative withdraw values
            return
        if int(amount) > int(self._funds):
            print("You have insufficient funds to withdraw the requested amount")  # error checking for not enough funds
            return
        # call tid function
        tid = calculate_tid()

        #  open the transactions file to append the new transaction
        with open("accountsTransactions.txt", "a") as file_reader:
            #  transaction is a line string with some details

            transaction = str(tid) + "_withdraw_" + self.IBAN + "_" + str(amount) + "_" + str(datetime.date.today())
            print(transaction, file=file_reader)  # print to the file
        self._transactions.append(str(tid))  # append id to transactions list to link to the account
        result = int(self._funds) - int(amount)
        self._funds = result  # remove funds as requested from account

    def deposit(self, amount):
        """deposit method for putting in money. error checking is done then the transaction is recorded
         and funds are added"""
        if int(amount) <= 0:
            print("You can only deposit a positive value")  # error validation for negative deposit values
            return

        # call tid function
        tid = calculate_tid()

        #  open the transactions file to append the new transaction
        with open("accountsTransactions.txt", "a") as file_reader:
            #  transaction is a line string with some details
            transaction = str(tid) + "_deposit_" + self.IBAN + "_" + str(amount) + "_" + str(datetime.date.today())
            print(transaction, file=file_reader)  # print to the file
        self._transactions.append(str(tid))  # append id to transactions list to link to the account
        result = int(self._funds) + int(amount)
        self._funds = result  # add funds as requested to account

    def receive_transfer(self, tid, amount):
        """receive transfer method for payee to receive transferred funds. transaction is appended to
        the transactions list attribute and details are updated"""
        self._transactions.append(str(tid))  # transaction id is appended to payee's list of transactions
        result = int(self._funds) + int(amount)
        self._funds = result  # funds are added to the account
        self.update_details()

    def transfer(self, amount, IBAN):
        """transfer method for transferring money to other accounts. error checking is done first.
        afterwards, the passed IBAN must be validated to check if it exists or not.
        If it does the transfer is recorded, funds are removed from the account and added
        to the account corresponding with the IBAN"""
        if amount <= 0:
            print("You can only transfer a positive value")  # error validation for negative transfer values
            return

        if amount > self._funds:
            print("You have insufficient funds to transfer the requested amount")  # error checking for not enough funds
            return

        # IBAN validation to check if passed IBAN is valid/exists
        with open("accounts.txt", "r") as file_reader:
            for line in file_reader:
                # split string into list. the string contains account details separated with an underscore
                acc = line.strip().split("_")
                if IBAN == acc[3]:  # find the passed IBAN substring in the string
                    # call tid function
                    tid = calculate_tid()

                    #  open the transactions file to append the new transaction
                    with open("accountsTransactions.txt", "a") as line_reader:
                        #  transaction is a line string with some details
                        transaction = str(tid) + "_transfer_" + IBAN + "_" + str(amount) + "_" + str(datetime.date.today())
                        print(transaction, file=line_reader)  # print to the file

                    self._transactions.append(str(tid))
                    result = int(self._funds) - int(amount)
                    self._funds = result  # remove funds as requested from account

                    # create temporary account instance with list elements
                    if acc[1] == "savings":
                        payee = SavingsAccount(acc[0], acc[1], acc[2], acc[3], acc[4], acc[5])
                    else:
                        payee = CheckingAccount(acc[0], acc[1], acc[2], acc[3], acc[4], acc[5], acc[6])
                    payee.receive_transfer(tid, amount)  # pass tid and amount into receive_transfer method
                    self.update_details()
                    return
            print("IBAN does not exist")  # indicate IBAN does not exist to the user
            return

    def view_transactions(self):
        """method to print transactions associated to the account"""
        if self._transactions == []:
            print("No transactions available")
            return
        print("Transfer ID      Type         IBAN          Amount        Date")
        print(60*"-")
        with open("accountsTransactions.txt", "r") as t_reader:
            for line in t_reader:
                t_details = line.strip().split("_")
                if t_details[0] in self._transactions:
                    print("{:15s}{:15s}{:15s}{:15s}{:15s}".format(t_details[0], t_details[1], t_details[2], t_details[3], t_details[4]))

    def update_details(self):
        """method to write all the object details back to the account txt file.
        a temp file is used to write all the existing data except the outdated data which
        is overwritten by the current running objects. The object attributes are converted into a single line
        string format to be written to the txt file"""
        with open("accounts.txt", "r") as account_reader, open("accountstemp.txt", "w") as temp_reader:  # temp file to write data plus the updates to
            for line in account_reader:
                accounts = line.strip().split("_")
                # write data normally until an account line matches our current one
                # the current one(the most up to date) will replace the account line to be written to the temp file
                if accounts[0] == self._acc_number:
                    account = str(self._acc_number) + "_" + self._name + "_" + self.IBAN + "_" + str(self._funds) + "_" + self.get_transactionlist() + "\n"  # format account atrributes into a string
                    temp_reader.write(account)
                else:
                    temp_reader.write(line)

        with open("accountstemp.txt", "r") as temp_reader, open("accounts.txt", "w") as file_reader:  # copy the contents of the temp file back to main accounts
            for line in temp_reader:
                file_reader.write(line)
        os.remove("accountstemp.txt")

    def __str__(self):
        """str method for when class is called to print"""
        result = "Account Number: {:6s} Name: {:10s} IBAN: {:16s}".format(self._acc_number, self._name, self.IBAN)
        return result


class SavingsAccount(Account):
    """An account type object inheriting from the Account class. It defines a SavingsAccount.
    Works the same as the Account class except there is a limit of 1 withdrawal/transfer
    transaction per month"""
    def __init__(self, acc_number, acctype, name, IBAN, funds, transactions="None"):
        Account.__init__(self, acc_number, name, IBAN, funds, transactions)
        self._acctype = acctype

    def get_type(self):
        """get method for returning the account type"""
        return self._acctype

    def withdraw(self, amount):
        """the same as withdraw from Account class but with added validation.
        The transactions of the savings account is checked. Their dates are loaded onto a list
        and the most recent element's month is compared with the system/current month.
        If they are the same then the method will not proceed"""
        # validation for savings account
        # checks the most recent transfer/withdraw transaction date and compares it with current month
        # the limit is once per month so if they are the same then we return back to the menu
        datelist = []
        with open("accountsTransactions.txt", "r") as t_reader:
            for line in t_reader:  # iterate through each line of the file
                tran = line.strip().split("_")  # split string into a list of the transaction details

                # tran[0] contains the tid(transaction id) of a transaction
                # tran[1] contains the transaction type
                # if tran[0] is in the account's list of transaction id's and the type is withdraw or transfer
                # we go into the suite
                if tran[0] in self._transactions and (tran[1] == "withdraw" or tran[1] == "transfer"):
                    print(datelist)
                    print(tran)
                    datelist.append(str(tran[4]))  # append the date to a list
        if datelist:
            print(datelist)
            tdate = datelist[len(datelist) - 1]  # most recent date will be the last element of the list
            tdate = tdate.split("-")  # split the date into year, month, day
            today = datetime.date.today()  # retrieve current month date
            if tdate[1] == str(today.month):  # compare both months
                print("Savings accounts are restricted to only one withdrawal or transfer per month. Your limit of 1"
                      " has already been exceeded")  # error message for user
                return
        Account.withdraw(self, amount)

    def transfer(self, amount, IBAN):
        """same as transfer from account class but with added validation.
        The transactions of the savings account is checked. Their dates are loaded onto a list
        and the most recent element's month is compared with the system/current month.
        If they are the same then the method will not proceed"""
        # validation for savings account
        # checks the most recent transfer/withdraw transaction date and compares it with current month
        # the limit is once per month so if they are the same then we return back to the menu
        datelist = []
        with open("accountsTransactions.txt", "r") as t_reader:
            for line in t_reader:  # iterate through each line of the file
                tran = line.strip().split("_")  # split string into a list of the transaction details

                # tran[0] contains the tid(transaction id) of a transaction
                # tran[1] contains the transaction type
                # if tran[0] is in the account's list of transaction id's and the type is withdraw or transfer
                # we go into the suite
                if tran[0] in self._transactions and (tran[1] == "withdraw" or tran[1] == "transfer"):
                    datelist.append(str(tran[4]))  # append the date to a list
        if datelist:
            tdate = datelist[len(datelist) - 1]  # most recent date will be the last element of the list
            tdate = tdate.split("-")  # split the date into year, month, day
            today = datetime.date.today()  # retrieve current month date
            if tdate[1] == str(today.month):  # compare both months
                print("Savings accounts are restricted to only one withdrawal or transfer per month. Your limit of 1"
                      "has already been exceeded")  # error message for user
                return
        Account.transfer(self, amount, IBAN)

    def __str__(self):
        result = "Account Number: {:6s} Type: {:10s} Name: {:10s} IBAN: {:16s}".format(self._acc_number, self._acctype, self._name, self.IBAN)
        return result

    def update_details(self):
        with open("accounts.txt", "r") as account_reader, open("accountstemp.txt", "w") as temp_reader:  # temp file to write data plus the updates to
            for line in account_reader:
                accounts = line.strip().split("_")
                # write data normally until an account line matches our current one
                # the current one(the most up to date) will replace the account line to be written to the temp file
                if accounts[0] == self._acc_number:
                    account = str(self._acc_number) + "_" + self._acctype + "_" + self._name + "_" + self.IBAN\
                              + "_" + str(self._funds) + "_" +\
                              self.get_transactionlist() + "\n" # format account atrributes into a string
                    temp_reader.write(account)
                else:
                    temp_reader.write(line)

        with open("accountstemp.txt", "r") as temp_reader, open("accounts.txt", "w") as file_reader:  # copy the contents of the temp file back to main accounts
            for line in temp_reader:
                file_reader.write(line)
        os.remove("accountstemp.txt")


class CheckingAccount(Account):
    """An account type subclass of account. Everything is the same except for some formatting and the added credit limit"""
    def __init__(self, acc_number, acctype, name, IBAN, funds, transactions="None", creditlimit=-1000):
        Account.__init__(self, acc_number, name, IBAN, funds, transactions)
        self._acctype = acctype
        self._creditlimit = creditlimit  # specified credit limit for negative balance

    def get_type(self):
        return self._acctype

    def get_limit(self):
        return self._creditlimit

    def withdraw(self, amount):  # method for taking money out of the checking account
        if int(amount) <= 0:
            print("You can only withdraw a positive value")  # error validation for negative withdraw values
            return
        if amount > abs(int(self._creditlimit)) + int(self._funds):
            # error checking for not enough funds with credit limit added on for the checking account
            print("You have insufficient funds to withdraw the requested amount")
            return
        # call tid function
        tid = calculate_tid()

        #  open the transactions file to append the new transaction
        with open("accountsTransactions.txt", "a") as file_reader:
            #  transaction is a line string with some details
            transaction = str(tid) + "_withdraw_" + self.IBAN + "_" + str(amount) + "_" + str(datetime.date.today())
            print(transaction, file=file_reader)  # print to the file
        self._transactions.append(str(tid))  # append id to transactions list to link to the account
        result = int(self._funds) - int(amount)
        self._funds = result  # remove funds as requested from account

    def transfer(self, amount, IBAN):
        if int(amount) <= 0:
            print("You can only transfer a positive value")  # error validation for negative transfer values
            return

        if amount > abs(int(self._creditlimit)) + int(self._funds):
            # error checking for not enough funds with credit limit added on for the checking account
            print("You have insufficient funds to withdraw the requested amount")
            return

        # IBAN validation to check if passed IBAN is valid/exists
        with open("accounts.txt", "r") as file_reader:
            for line in file_reader:
                # split string into list. the string contains account details separated with an underscore
                acc = line.strip().split("_")
                print(acc)
                if IBAN == acc[3]:  # find the passed IBAN substring in the string
                    # call tid function
                    tid = calculate_tid()

                    #  open the transactions file to append the new transaction
                    with open("accountsTransactions.txt", "a") as line_reader:
                        #  transaction is a line string with some details
                        transaction = str(tid) + "_transfer_" + IBAN + "_" + str(amount) + "_" + str(datetime.date.today())
                        print(transaction, file=line_reader)  # print to the file

                    self._transactions.append(str(tid))
                    sub = int(self._funds) - int(amount)
                    self._funds = str(sub)

                    # create temporary account instance with list elements
                    if acc[1] == "savings":
                        payee = SavingsAccount(acc[0], acc[1], acc[2], acc[3], acc[4], acc[5])
                    else:
                        payee = CheckingAccount(acc[0], acc[1], acc[2], acc[3], acc[4], acc[5], acc[6])
                    payee.receive_transfer(tid, amount)  # pass tid and amount into receive_transfer method
                    self.update_details()
                    return
            print("IBAN does not exist")  # indicate IBAN does not exist to the user
            return

    def __str__(self):
        result = "Account Number: {:6s} Type: {:10s} Name: {:10s} IBAN: {:16s}".format(self._acc_number, self._acctype, self._name, self.IBAN)
        return result

    def update_details(self):  # method to write all the object details back to the account txt file
        with open("accounts.txt", "r") as account_reader, open("accountstemp.txt", "w") as temp_reader:  # temp file to write data plus the updates to
            for line in account_reader:
                accounts = line.strip().split("_")
                # write data normally until an account line matches our current one
                # the current one(the most up to date) will replace the account line to be written to the temp file
                if accounts[0] == self._acc_number:
                    account = str(self._acc_number) + "_" + self._acctype + "_" + self._name + "_" + self.IBAN\
                              + "_" + str(self._funds) + "_" + self.get_transactionlist() + "_"\
                              + str(self._creditlimit) + "\n" # format account atrributes into a string
                    temp_reader.write(account)
                else:
                    temp_reader.write(line)

        with open("accountstemp.txt", "r") as temp_reader, open("accounts.txt", "w") as file_reader:  # copy the contents of the temp file back to main accounts
            for line in temp_reader:
                file_reader.write(line)
        os.remove("accountstemp.txt")


class Customer(object):
    """General Bank Customer class with private attributes and composition for accounts"""
    def __init__(self, customerid, pin, firstname, lastname, age, accounts="None"):
        self.__customerid = customerid
        self.__PIN = pin  # private pin for customer login
        self.__firstname = firstname
        self.__lastname = lastname
        self.__age = age
        if accounts == "None":
            self.__accounts = []
        else:
            self.__accounts = accounts  # assign list of account numbers to the accounts attribute
            with open("accounts.txt", "r") as account_reader:
                accounttemp = []  # temp list for account instances
                for line in account_reader:  # read every account line
                    acclist = line.strip().split("_")  # split line into list of account details
                    if acclist[0] in self.__accounts:  # check if the read account number matches an element in the list
                        if acclist[1] == "savings":  # create the appropriate account object by checking the type
                            accounttemp.append(SavingsAccount(acclist[0], acclist[1], acclist[2], acclist[3], int(acclist[4]), acclist[5]))
                        else:
                            accounttemp.append(CheckingAccount(acclist[0], acclist[1], acclist[2], acclist[3], int(acclist[4]), acclist[5], acclist[6]))
                self.__accounts = accounttemp  # assign temp list back to customer accounts attribute

    def __str__(self):
        result = "Customer ID: " + self.__customerid + "\n" + "Firstname" + self.__firstname + "\n" + "Lastname: " + \
                 self.__lastname + "\n" + "Age: " + self.__age + "\n"
        return result

    def get_custno(self):
        return self.__customerid

    def get_name(self):
        return self.__firstname

    def get_accounts(self):
        return self.__accounts

    def get_accountlist(self):
        """same as get_transactionslist from account class"""
        accountlist = ''  # format the transaction list into a writeable string
        for t, l in enumerate(self.__accounts):
            if t == (len(self.__accounts) - 1):  # end of line to not append a comma
                accountlist += str(self.__accounts[t].get_acc())
            else:
                accountlist += str(self.__accounts[t].get_acc()) + ","  # separate each element(transaction id) with a comma
        return accountlist

    def new_account(self, name, acctype):
        """method for creating new account for customer object. error checking is done
        and then a new account number and IBAN is calculated. The new account object is then created and
        linked to the current customer instance"""
        if acctype == "2" and self.__age < "18":
            print("Customer Age is not above 18 for a checking account")
            return
        # open the accounts file in order to calculate the new account number id
        with open("accounts.txt", "r") as account_reader:
            aid = 0
            for aid, l in enumerate(account_reader):  # counts the number of lines in the file
                pass
            if aid == 0:
                try:  # exception for first line of txt file
                    l
                    aid += 2
                except NameError:  # if file is empty
                    l = None
                    aid += 1
            else:
                aid += 2  # each line is an account so the no. of lines plus 2 indicates the next line/id

        # determine new IBAN
        used = False
        while True:
            num = random.randint(1, 99999)  # random number up to 5 digits
            IBAN = "IE" + str(num)  # cast as a string and add IE identifier
            # check if already used
            with open("accounts.txt", "r") as account_reader:
                for line in account_reader:
                    acclist = line.strip().split("_")
                    if IBAN == acclist[3]:
                        used = True
            if used is False:
                break

        match acctype:  # switch statement equivalent from c
            case "1":  # creating a new SavingsAccount
                with open("accounts.txt", "a") as account_reader:
                    #  write the account line that is to be written to the accounts file
                    account = str(aid) + "_savings_" + name + "_" + IBAN + "_" + "0" + "_" + "None"
                    account_reader.write(account)  # output to file
                    self.__accounts.append(SavingsAccount(str(aid), "savings", name, IBAN, 0, "None"))
            case "2":  # creating a new CheckingAccount
                with open("accounts.txt", "a") as account_reader:
                    #  write the account line that is to be written to the accounts file
                    account = str(aid) + "_checking_" + name + "_" + IBAN + "_" + "0" + "_" + "None" + "_" + "-1000"
                    print(account, file=account_reader)  # output to file
                    self.__accounts.append(CheckingAccount(str(aid), "checking", name, IBAN, 0, "None", -1000))
        print("Account created successfully")
        print(self.__accounts[len(self.__accounts) - 1])

    def delete_account(self):
        """method for deleting customer's account. The account is already delinked from the customer and
        so the customer details must be updated using the new account list"""
        accountlist = ''  # format the account list into a writeable string
        for t, l in enumerate(self.__accounts):
            if t == (len(self.__accounts) - 1):  # end of line to not append a comma
                accountlist += str(self.__accounts[t].get_acc())
            else:
                accountlist += str(self.__accounts[t].get_acc()) + ","  # separate each element(account number) with a comma
        with open("customers.txt", "r") as c_reader, open("customerstemp.txt", "w") as temp_reader:
            for line in c_reader:
                customers = line.strip().split("_")
                # write data normally until a customer line matches our current one
                # the current one(the most up to date) will replace the customer line to be written to the temp file
                if customers[0] == self.__customerid:
                    customer = str(self.__customerid) + "_" + self.__PIN + "_" + self.__firstname + "_" + self.__lastname \
                              + "_" + str(self.__age) + "_" + accountlist + "\n"  # format customer atrributes into a string
                    temp_reader.write(customer)
                else:
                    temp_reader.write(line)

        with open("customerstemp.txt", "r") as temp_reader, open("customers.txt", "w") as file_reader:  # copy the contents of the temp file back to main customers
            for line in temp_reader:
                file_reader.write(line)
        os.remove("customerstemp.txt")

    def update_details(self):
        """method to write all the object details back to the account and customer txt file"""
        with open("accounts.txt", "r") as account_reader, open("accountstemp.txt", "w") as temp_reader:  # temp file to write data plus the updates to
            for line in account_reader:
                accounts = line.strip().split("_")
                # write data normally until an account line matches our current one
                # the current one(the most up to date) will replace the account line to be written to the temp file
                account = ""
                for acc in self.__accounts:
                    if accounts[0] == acc.get_acc():
                        if accounts[1] == "savings":
                            account = str(acc.get_acc()) + "_" + acc.get_type() + "_" + acc.get_name() + "_" + acc.IBAN\
                                      + "_" + str(acc.get_balance()) + "_" + \
                                      acc.get_transactionlist() + "\n"  # format account atrributes into a string
                            temp_reader.write(account)
                            break
                        else:
                            # format account atrributes into a string
                            account = str(acc.get_acc()) + "_" + acc.get_type() + "_" + acc.get_name() + "_" + acc.IBAN\
                                      + "_" + str(acc.get_balance()) + "_" + \
                                      acc.get_transactionlist() + "_" + acc.get_limit() + "\n"
                            temp_reader.write(account)
                            break
                if account == "":  # else write normally
                    temp_reader.write(line)

        with open("accountstemp.txt", "r") as temp_reader, open("accounts.txt", "w") as file_reader:  # copy the contents of the temp file back to main accounts
            for line in temp_reader:
                file_reader.write(line)
        os.remove("accountstemp.txt")

        accountlist = ''  # format the account list into a writeable string
        for t, l in enumerate(self.__accounts):
            if t == (len(self.__accounts) - 1):  # end of line to not append a comma
                accountlist += str(self.__accounts[t].get_acc())
            else:
                accountlist += str(
                    self.__accounts[t].get_acc()) + ","  # separate each element(account number) with a comma
        with open("customers.txt", "r") as c_reader, open("customerstemp.txt", "w") as temp_reader:
            for line in c_reader:
                customers = line.strip().split("_")
                # write data normally until a customer line matches our current one
                # the current one(the most up to date) will replace the customer line to be written to the temp file
                if customers[0] == self.__customerid:
                    customer = str(
                        self.__customerid) + "_" + self.__PIN + "_" + self.__firstname + "_" + self.__lastname \
                               + "_" + str(
                        self.__age) + "_" + accountlist + "\n"  # format customer atrributes into a string
                    temp_reader.write(customer)
                else:
                    temp_reader.write(line)

        with open("customerstemp.txt", "r") as temp_reader, open("customers.txt",
                                                                 "w") as file_reader:  # copy the contents of the temp file back to main customers
            for line in temp_reader:
                file_reader.write(line)
        os.remove("customerstemp.txt")


def main():
    """Function for program start. Calls the menu function"""
    print("Welcome to Kieran's Bank\n")  # welcome the user
    while input("Hit 'Enter' to login") != "":
        pass
    with open("customers.txt", "r") as line_reader:  #prompt user login and check if details are correct
        while True:
                id = input("\nCustomer ID: ")
                for line in line_reader:  # go through each line to check the customer id
                    customer = line.strip().split("_")
                    if customer[0] == id:
                        break
                if customer[0] == id:  # proceed into menu function to begin session
                    while True:
                        pin = input("PIN: ")
                        if pin == "q":
                            break
                        if customer[1] == pin:
                            menu(customer)  # pass list of customer details
                            break
                        else:
                            print("PIN incorrect. Try Again or 'q' to quit")
                            continue
                else:
                    print("Customer ID does not exist, Please Try Again")
                    continue

                print("Session Ended. Thank You")
                break


def calculate_tid():
    """function for calculating the new transaction id by counting the number of lines in the txt file"""
    # open the transactions file in order to calculate the transaction id
    with open("accountsTransactions.txt", "r") as file_reader:
        tid = 0
        for tid, l in enumerate(file_reader):  # counts the number of lines in the file
            pass
        if tid == 0:
            try:  # exception for first line of txt file
                l
                tid += 2
            except NameError:  # if file is empty
                l = None
                tid += 1
        else:
            tid += 2  # each line is a transaction so the no. of lines plus 2 indicates the next line/id
    return tid


def menu(customer):
    """menu function for displaying all the options that access the methods"""
    customer[5] = customer[5].strip().split(",")  # convert account numbers string to list
    accountlist = customer[5]  # grabbing list of accounts for delete account method in customer
    customer = Customer(customer[0], customer[1], customer[2], customer[3], customer[4], customer[5])
    test = customer.get_accounts()
    print(test[0].get_transactionlist())
    while True:
        print("Welcome", customer.get_name())  # main menu options format
        print(30*"-")
        print("1)\tCreate New Account")
        print("2)\tView Transactions")
        print("3)\tBalance")
        print("4)\tDeposit")
        print("5)\tWithdraw")
        print("6)\tTransfer")
        print("7)\tDelete an Account")
        print("8)\tExit")
        user_choice = int(input("Select a menu option: "))
        match user_choice:  # C switch statement equivalent for each menu option (NOTE: Python 3.10 required)
            case 1:  # Create New Account
                while True:  # loop for error validation
                    print(30*"-")
                    print("1) Savings Account")
                    print("2) Checking Account")
                    type = str(input("What type of account would you like to create?:"))
                    if type not in ["1", "2"]:
                        print("Not a valid option")
                        continue  # reloop and prompt again
                    break  # break out loop and proceed
                name = input("What name would you like for your account?\n")
                customer.new_account(name, type)  # pass name and type into customer method

            case 2:  # View Transactions
                while True:  # error loop
                    print(30 * "-")
                    accounts = customer.get_accounts()  # assign accounts into an accounts list
                    for i, l in enumerate(accounts):
                        print(i + 1,")", accounts[i])  # show accounts
                    while True:
                        index = input("Which account's transactions would you like to view?")
                        try:
                            index = int(index)
                        except ValueError:
                            print("Not a valid option")
                            continue
                        break

                    if int(index) not in range(1, len(accounts) + 1):
                        print("Not a valid option")
                        continue
                    break
                accounts[index - 1].view_transactions()

            case 3:  # Balance
                while True:
                    print(30 * "-")
                    accounts = customer.get_accounts()  # assign accounts into an accounts list
                    for i, l in enumerate(accounts):
                        print(i + 1,")", accounts[i])  # show accounts
                    while True:
                        index = input("Which account balance would you like to view?")
                        try:
                            index = int(index)
                        except ValueError:
                            print("Not a valid option")
                            continue
                        break
                    if int(index) not in range(1, len(accounts) + 1):
                        print("Not a valid option")
                        continue
                    break
                balance = accounts[index - 1].get_balance()
                print("Balance :", balance)

            case 4:  # Deposit
                while True:
                    print(30 * "-")
                    accounts = customer.get_accounts()  # assign accounts into an accounts list
                    for i, l in enumerate(accounts):
                        print(i + 1,")", accounts[i])  # show accounts
                    while True:
                        index = input("Which account would you like to deposit money in?")
                        try:
                            index = int(index)
                        except ValueError:
                            print("Not a valid option")
                            continue
                        break
                    if int(index) not in range(1, len(customer.get_accounts()) + 1):
                        print("Not a valid option")
                        continue
                    break
                while True:
                    amount = input("How much would you like to deposit? (Whole numbers only)")
                    try:
                        amount = int(amount)
                    except ValueError:
                        print("Not a valid number")
                        continue
                    break
                accounts[index - 1].deposit(amount)

            case 5:  # Withdraw
                while True:
                    print(30 * "-")
                    accounts = customer.get_accounts()  # assign accounts into an accounts list
                    for i, l in enumerate(accounts):
                        print(i + 1,")", accounts[i])  # show accounts
                    while True:
                        index = input("Which account would you like to withdraw money from?")
                        try:
                            index = int(index)
                        except ValueError:
                            print("Not a valid option")
                            continue
                        break
                    if int(index) not in range(1, len(customer.get_accounts()) + 1):
                        print("Not a valid option")
                        continue
                    break
                while True:
                    amount = input("How much would you to like withdraw? (Whole numbers only)\n")
                    try:
                        amount = int(amount)
                    except ValueError:
                        print("Not a valid number")
                        continue
                    break
                accounts[index - 1].withdraw(amount)

            case 6:  # Transfer
                while True:
                    print(30 * "-")
                    accounts = customer.get_accounts()  # assign accounts into an accounts list
                    for i, l in enumerate(accounts):
                        print(i + 1,")", accounts[i])  # show accounts
                    while True:
                        index = input("Which account would you like to transfer money from?\n")
                        try:
                            index = int(index)
                        except ValueError:
                            print("Not a valid option")
                            continue
                        break
                    if int(index) not in range(1, len(customer.get_accounts()) + 1):
                        print("Not a valid option")
                        continue
                    break
                while True:
                    amount = input("How much would you to like transfer? (Whole numbers only)\n")
                    try:
                        amount = int(amount)
                    except ValueError:
                        print("Not a valid number")
                        continue
                    break
                iban = input("IBAN for the money to be transferred to:\n")
                accounts[index - 1].transfer(amount, iban)
            case 7:  # Delete an Account
                while True:
                    print(30 * "-")
                    accounts = customer.get_accounts()  # assign accounts into an accounts list
                    for i, l in enumerate(accounts):
                        print(i + 1,")", accounts[i])  # show accounts
                    while True:
                        index = input("Which account would you like to delete?")
                        try:
                            index = int(index)
                        except ValueError:
                            print("Not a valid option")
                            continue
                        break
                    if int(index) not in range(1, len(customer.get_accounts()) + 1):
                        print("Not a valid option")
                        continue
                    break
                accounts.pop(index - 1)  # account is removed from accounts list
                customer.delete_account()  # method to update details with new list called
            case 8:  # Exit
                print(30 * "-")
                customer.update_details()  # all details updated before program exit
                return  # return back to main where the program ends
            case _:
                print("not a valid option\n")
                continue

# begin program
main()
