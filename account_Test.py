import unittest
from flask import Flask, render_template, request, url_for, redirect
from app import app
from model import db

class AccountTestCases(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        app.config["SERVER_NAME"] = "stefan.se"
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["WTF_CSRF_METHODS"] = []
        app.config["TESTING"] = True



    def test_withdraw_more_than_15000(self):
        test_client = app.test_client()
        url = '/deposit&withdraw'
        with test_client:
            response = test_client.post(url, data={ "fromAccount": 12, "choice":"Withdraw", "amount": 20000 })
            assert response.status_code != 302




    def test_deposit_more_than_15000(self):
        test_client = app.test_client()
        url = '/deposit&withdraw'
        with test_client:
            response = test_client.post(url, data={"fromAccount":"12", "choice":"Deposit", "amount":"11122"  })
            assert response.status_code == 302

   

    def test_withdraw_negative_money(self):
        test_client = app.test_client()
        url = '/deposit&withdraw'
        with test_client:
            response = test_client.post(url, data={"fromAccount":"12", "choice":"Withdraw", "amount":"11122"  })
            assert response.status_code == 302
   


    def test_transfer_more_than_balance(self):
        test_client = app.test_client()
        url = '/transfer'
        with test_client:
            response = test_client.post(url, data={ "fromAccount":"12", "toAccount":"13", "amount":"11122" })
            assert response.status_code == 302







if __name__ == "__main__":
    unittest.main()
