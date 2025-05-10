from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from datetime import date

class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    course = SelectField('Course', choices=[
        ('Computer Science', 'Computer Science'),
        ('Electrical Engineering', 'Electrical Engineering'),
        ('Mechanical Engineering', 'Mechanical Engineering'),
        ('Civil Engineering', 'Civil Engineering'),
        ('Business Administration', 'Business Administration')
    ], validators=[DataRequired()])
    submit = SubmitField('Register')
    
    def validate_date_of_birth(self, field):
        if field.data > date.today():
            raise ValidationError('Date of birth cannot be in the future')

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')