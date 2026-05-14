import os
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class GuideForm(FlaskForm):
    type = SelectField('Тип', choices=['guide', 'challenge'], validators=[DataRequired()])
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    images = SelectMultipleField('Картинки', choices=[])
    submit = SubmitField('Опубликовать')