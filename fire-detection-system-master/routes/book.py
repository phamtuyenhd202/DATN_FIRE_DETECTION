from flask import Blueprint, g, escape, session, redirect, render_template, request, jsonify, Response, url_for
from app import DAO

from Controllers.UserManager import UserManager
from Controllers.BookManager import BookManager

book_view = Blueprint('book_routes', __name__, template_folder='/templates')

book_manager = BookManager(DAO)
user_manager = UserManager(DAO)

@book_view.route('/notification', methods=['GET'])
@user_manager.user.login_required
def list_books():
    print("lỗi")
    user_manager.user.set_session(session, g)
    books = book_manager.list()
    return render_template("books_manage.html", books=books, g=g)

@book_view.route('/notification/add', methods=['GET', 'POST'])
@user_manager.user.login_required
def add_book():
    user_manager.user.set_session(session, g)
    if request.method == 'POST':
        name = request.form.get('name')
        noti_email = request.form.get('noti_email')
        book_manager.add(name, noti_email)
        return redirect(url_for('book_routes.list_books'))
    return render_template("book_form.html", action="Add", g=g)

@book_view.route('/notification/edit/<int:id>', methods=['GET', 'POST'])
@user_manager.user.login_required
def edit_book(id):
    user_manager.user.set_session(session, g)
    book = book_manager.get(id)
    if request.method == 'POST':
        name = request.form.get('name')
        noti_email = request.form.get('noti_email')
        book_manager.update(id, name, noti_email)
        return redirect(url_for('book_routes.list_books'))
    return render_template("book_form.html", action="Edit", book=book, g=g)

@book_view.route('/notification/delete/<int:id>', methods=['POST'])
@user_manager.user.login_required
def delete_book(id):
    user_manager.user.set_session(session, g)
    book_manager.delete(id)
    return redirect(url_for('book_routes.list_books'))

