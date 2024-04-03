from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, URLField, SubmitField, SelectField
from wtforms.validators import DataRequired
from wtforms.fields import DateField
from models import Image, Category
from datetime import date


class ReportForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    image_id = SelectField('Выберите картинку', coerce=int)
    url = URLField('URL отчета', validators=[DataRequired()])
    date_posted = DateField('Дата публикации', format='%Y-%m-%d', default=date.today, validators=[DataRequired()])
    category_id = SelectField('Категория', coerce=int, choices=[])
    submit = SubmitField('Сохранить')

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.image_id.choices = [(img.id, img.description) for img in Image.query.all()]
        for img in Image.query.all():
            image_option = self.image_id.choices[img.id - 1]  # Индекс может отличаться, если id не начинаются с 1
            self.image_id.choices[img.id - 1] = (image_option[0], image_option[1], {'data-img-path': img.file_path})
        self.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]


class CategoryForm(FlaskForm):
    name = StringField('Название категории', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

