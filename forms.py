import decimal

from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
import datetime


class LessThan(object):
    """
    Compares the values of two fields.

    :param fieldname:
        The name of the other field to compare to.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated with `%(other_label)s` and `%(other_name)s` to provide a
        more helpful error.
    """
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        if field.data > other.data:
            d = {
                'other_label': hasattr(other, 'label') and other.label.text or self.fieldname,
                'other_name': self.fieldname
            }
            message = self.message
            if message is None:
                message = field.gettext('Field must be less than to %(other_name)s.')
            raise StopValidation(message % d)


class CourseForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(),
                                             Length(min=10, max=100)])
    description = TextAreaField('Course Description',
                                validators=[InputRequired(),
                                            Length(max=200)])
    price = IntegerField('Price', validators=[InputRequired()])
    level = RadioField('Level',
                       choices=['Beginner', 'Intermediate', 'Advanced'],
                       validators=[InputRequired()])
    available = BooleanField('Available', default='checked')


class NavigationForm(FlaskForm):
    coin1 = SelectField('Coin1', choices=[('Bitcoin', 'Bitcoin'), ('Ethereum', 'Ethereum'), ('Litecoin', 'Litecoin'), ('Bitcoin Cash', 'Bitcoin Cash'), ('Ripple', 'Ripple')], validators=[InputRequired()], default="Bitcoin")
    coin2 = SelectField('Coin2', choices=[('Bitcoin', 'Bitcoin'), ('Ethereum', 'Ethereum'), ('Litecoin', 'Litecoin'), ('Bitcoin Cash', 'Bitcoin Cash'), ('Ripple', 'Ripple')], validators=[InputRequired()], default="Ethereum")
    function = SelectField('Function', choices=[('Backtest', 'Backtest'), ('Analyze', 'Analyze'), ('Graph', 'Graph')], validators=[InputRequired()], default="Graph")

    minimum_date = datetime.datetime.fromisoformat("2020-06-06")
    today = (datetime.datetime.today() - datetime.timedelta(days=1)).date()
    date1 = DateField('Start Date', validators=[InputRequired()], default=minimum_date)
    date2 = DateField('End Date', validators=[InputRequired()], default=today)

    def validate_enddate_field(form, field):
        if field.data < form.date1.data:
            raise ValidationError("End date must not be earlier than start date.")


class BacktestForm(FlaskForm):
    coin1 = SelectField('Coin1', choices=[('Bitcoin', 'Bitcoin'), ('Ethereum', 'Ethereum'), ('Litecoin', 'Litecoin'), ('Bitcoin Cash', 'Bitcoin Cash'), ('Ripple', 'Ripple')], validators=[InputRequired()], default="Bitcoin")
    coin2 = SelectField('Coin2', choices=[('Bitcoin', 'Bitcoin'), ('Ethereum', 'Ethereum'), ('Litecoin', 'Litecoin'), ('Bitcoin Cash', 'Bitcoin Cash'), ('Ripple', 'Ripple')], validators=[InputRequired()], default="Ethereum")
    function = SelectField('function', choices=[('Backtest', 'Backtest'), ('Analyze', 'Analyze'), ('Graph', 'Graph')], validators=[InputRequired()], default="Backtest")

    ma_period = IntegerField('Moving Average Period', validators=[InputRequired()])
    std_period = IntegerField('Standard Deviation Period', validators=[InputRequired()])
    max_duration = IntegerField('Maximum Trading Duration', validators=[InputRequired()])
    entry_threshold = DecimalRangeField('Entry Threshold',
                                         validators=[InputRequired(), NumberRange(min=0.2, max=3)],
                                         places=1)
    exit_threshold = DecimalRangeField('Exit Threshold',
                                        validators=[InputRequired(), NumberRange(min=0.1, max=2.9),
                                                    LessThan("entry_threshold")], places=1)
    sl_threshold = DecimalRangeField('Stop/Loss Threshold', validators=[InputRequired(), NumberRange(min=0, max=1)])

    minimum_date = datetime.datetime.fromisoformat("2020-06-06")
    today = (datetime.datetime.today() - datetime.timedelta(days=1)).date()
    date1 = DateField('Start Date', validators=[InputRequired()], default=minimum_date)
    date2 = DateField('End Date', validators=[InputRequired()], default=today)