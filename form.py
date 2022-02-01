from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, IntegerField, SelectField, RadioField, SubmitField
from wtforms.validators import DataRequired, ValidationError, NumberRange
from model import Account

class TransferForm(FlaskForm):
    fromAccount = StringField('From', validators=[DataRequired(message='Please choose a account')])
    toAccount = StringField('To', validators=[DataRequired(message='Please choose a account')])
    amount = IntegerField('Amount', validators=[DataRequired()])
    submit = SubmitField()
    
    def validate_amount(form, amount):
        choosenAccount = Account.query.filter(Account.id == int(form.fromAccount.data)).first()
        if amount.data >  choosenAccount.Balance:
            raise ValidationError("Amount is greater than the balance.")


class Deposit_Withdrawal_Form(FlaskForm):
    fromAccount = IntegerField('From', validators=[DataRequired(message='Please choose a account')])
    choice = RadioField('Choice option', validators=[DataRequired(message='Choose deposit or withdraw ')], choices=[('Deposit'), ('Withdraw') ])
    amount = IntegerField('Amount', validators=[DataRequired(), NumberRange( min= 1, max= 15000, message="Max amount $15,000") ])
    submit = SubmitField()

    def validate_amount(form, amount):
        choosenAccount = Account.query.filter(Account.id == int(form.fromAccount.data)).first()
        if (form.choice.data == "Withdraw" and amount.data >  choosenAccount.Balance):
            raise ValidationError("Amount is greater than the balance.")
    

