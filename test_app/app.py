"""Example view:
@app.route('/tests/')
def tests():
    test_item = Item.query.filter_by(item_type='test').first()
    return render_template('item.html',  item=test_item)
"""
import tempfile

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_nav.elements import Navbar, View
from werkzeug.datastructures import CombinedMultiDict

from .forms import *
from .setup import app, nav
from .ciphers import Ciphers, Deencrypter, Modes, default_key


test_app = Blueprint('test_app', __name__)


nav.register_element(
    'frontend_top',
    Navbar(
        View('TestApp', '.index'),
        View('De/En code', '.deencrypt'),
    )
)


@app.route('/')
def index():
    return render_template('index.html')


def process_form(form):
    if form.file_name.data:
        content = form.file_name.data.read()
    else:
        content = form.raw_text.data

    if not (form.file_name.data or form.raw_text.data):
        flash(f'Either raw text or filename should be passed', 'error')
        return None

    if form.key.data:
        key = form.key.data
    else:
        key = default_key()

    if not form.mode.raw_data:
        flash(f'Need to choose mode', 'error')
        return None
    if not form.cipher.raw_data:
        flash(f'Need to choose cipher', 'error')
        return None

    mode = Modes(form.mode.data)
    cipher = Ciphers(form.cipher.data)
    reverse = form.decrypt.data
    dnc = Deencrypter(cipher, mode, key)
    return dnc.decrypt(content) if reverse else dnc.encrypt(content)


@app.route('/deencrypt/', methods=['GET', 'POST'])
def deencrypt():
    form = DeencryptForm(CombinedMultiDict((request.files, request.form)))
    if request.method == 'POST':
        result = process_form(form)
        if result:
            tf = tempfile.NamedTemporaryFile()
            with open(tf.name, 'wb') as out:
                out.write(result)
            return send_file(tf, attachment_filename='result.blob', as_attachment=True)

    return render_template('deencrypt.html', form=form)


if __name__ == '__main__':
    # Run with: FLASK_DEBUG=1 FLASK_APP=test_app.app flask run
    app.run()
