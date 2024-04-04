from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Report, Image, Category
from flask import render_template, request, redirect, url_for, flash
from datetime import datetime
from forms import ReportForm, CategoryForm


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1330@localhost/stbti'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = ('b"\xf3\xb3\x1e\xac\x39\x92\xd4\x90\x8d\xeb\x12\xfa\xb0\xee\xec['
                            '\xbb\x1d\xfb\xae\x14\x9b\xa0\x9f"')


db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def index():
    reports = Report.query.all()
    return render_template('index.html', reports=reports)


@app.route('/add-report', methods=['GET', 'POST'])
def add_report():
    form = ReportForm()
    images = Image.query.all()
    category_id = request.args.get('category_id', None, type=int)
    categories = Category.query.order_by(Category.order.asc()).all()
    if form.validate_on_submit():

        max_order = db.session.query(db.func.max(Report.order)).filter_by(
            category_id=form.category_id.data).scalar() or 0
        new_report = Report(
            title=form.title.data,
            image_id=form.image_id.data,
            url=form.url.data,
            date_posted=form.date_posted.data,
            category_id=form.category_id.data,
            order=max_order + 1
        )
        db.session.add(new_report)
        db.session.commit()
        flash('Отчет успешно добавлен!', 'success')
        return redirect(url_for('index'))  # или другая целевая страница после добавления
    return render_template('add_report.html', form=form, images=images, category_id=category_id, categories=categories)


@app.route('/edit-report/<int:report_id>', methods=['GET', 'POST'])
def edit_report(report_id):
    report = Report.query.get_or_404(report_id)
    form = ReportForm(obj=report)

    if request.method == 'POST' and form.validate_on_submit():
        report.title = form.title.data
        report.image_id = form.image_id.data
        report.url = form.url.data
        report.date_posted = form.date_posted.data
        report.category_id = form.category_id.data
        db.session.commit()
        flash('Отчет успешно обновлен!', 'success')
        return redirect(url_for('index'))

    elif request.method == 'GET':
        form.title.data = report.title
        form.image_id.data = report.image_id
        form.url.data = report.url
        form.date_posted.data = report.date_posted
        form.category_id.data = report.category_id

    return render_template('edit_report.html', form=form)


@app.route('/manage-reports')
# @login_required
def manage_reports():
    categories = Category.query.order_by(Category.order.asc()).all()
    sorted_reports = {category.id: sorted(category.reports, key=lambda report: report.order) for category in categories}
    return render_template('manage_reports.html', categories=categories, sorted_reports=sorted_reports, Report=Report)


@app.route('/report/delete/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    try:
        db.session.delete(report)
        db.session.commit()
        flash('Отчет успешно удален!', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Произошла ошибка при попытке удаления отчета.', 'error')
    return redirect(url_for('index'))


@app.route('/update-report-order-and-category', methods=['POST'])
# @login_required
def update_report_order_and_category():
    data = request.get_json()
    for reportData in data:
        report = Report.query.get(reportData['id'])
        if report:
            report.order = reportData['order']
            report.category_id = reportData['new_category_id']
    db.session.commit()
    return jsonify({'message': 'Порядок и категории отчетов обновлены.'})


@app.route('/category/add', methods=['GET', 'POST'])
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        existing_category = Category.query.filter_by(name=form.name.data).first()
        if existing_category:
            flash('Категория с таким именем уже существует.', 'warning')
            return redirect(url_for('add_category'))

        max_order = db.session.query(db.func.max(Category.order)).scalar() or 0
        category = Category(name=form.name.data, order=max_order + 1)
        try:
            db.session.add(category)
            db.session.commit()
            flash('Категория успешно добавлена!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Ошибка при добавлении категории.', 'error')

        return redirect(url_for('add_category'))
    return render_template('add_category.html', form=form)


@app.route('/category/edit/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Категория обновлена успешно!')
        return redirect(url_for('add_category'))
    return render_template('add_category.html', form=form)


@app.route('/category/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Категория удалена успешно!'})


@app.route('/category/update_order', methods=['POST'])
def update_category_order():
    try:
        orderData = request.get_json()
        for index, category_id in enumerate(orderData, start=1):
            category = Category.query.get(category_id)
            if category:
                category.order = index
        db.session.commit()
        return jsonify({'message': 'Порядок категорий обновлен успешно!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/category/update_name', methods=['POST'])
def update_category_name():
    data = request.get_json()
    category = Category.query.get_or_404(data['id'])
    category.name = data['name']
    db.session.commit()
    return jsonify({'message': 'Имя категории обновлено успешно!'})


@app.route('/reports/<int:category_id>')
def reports_by_category(category_id):
    reports = Report.query.filter_by(category_id=category_id).all()
    category = Category.query.get(category_id)
    return render_template('reports_by_category.html', reports=reports, category=category, category_id=category_id)


@app.context_processor
def inject_categories():
    categories = Category.query.order_by(Category.order.asc()).all()
    return dict(categories=categories)


if __name__ == '__main__':
    app.run(debug=True)
