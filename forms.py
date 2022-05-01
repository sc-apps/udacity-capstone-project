from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, BooleanField, SelectField, DateField
from wtforms.validators import DataRequired

class AddForm(FlaskForm):
	child_name = StringField("Child's Name", validators=[DataRequired()])
	child_age = IntegerField("Child's Age", validators=[DataRequired()])
	gift_name = StringField("Gift's Name", validators=[DataRequired()])
	gift_link = StringField("Link to the Gift", validators=[DataRequired()])
	price = IntegerField("Gift's Price", validators=[DataRequired()])
	event_id = SelectField("Event", coerce=int, validators=[DataRequired()])
	shipping_address = TextAreaField("Shipping Address", validators=[DataRequired()])
	phone = StringField("Phone Number", validators=[DataRequired()])
	confirmation = BooleanField("I agree to provide my personal data to process the request.", validators=[DataRequired()])
	submit = SubmitField('Add Request')

# when a user clicks on request id, he can update all data except clild_name and child_age
# a user with Admin role can update all fields

class UpdateForm(FlaskForm):
	child_name = StringField("Child's Name", render_kw={'disabled':''}, validators=[DataRequired()])
	child_age = IntegerField("Child's Age", render_kw={'disabled':''}, validators=[DataRequired()])
	gift_name = StringField("Gift's Name", validators=[DataRequired()])
	gift_link = StringField("Link to the Gift", validators=[DataRequired()])
	price = IntegerField("Gift's Price", validators=[DataRequired()])
	shipping_address = TextAreaField("Shipping Address", validators=[DataRequired()])
	phone = StringField("Phone Number", validators=[DataRequired()])
	confirmation = BooleanField("I agree to provide my personal data to process the request.", validators=[DataRequired()])
	submit = SubmitField('Update Request')


# this form is only visible to users with Admin role
class AddEvent(FlaskForm):
	name = StringField("Event Name", validators=[DataRequired()])
	date = DateField("Planned Date", validators=[DataRequired()])
	submit = SubmitField('Add Event')


