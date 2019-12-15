"""Example form:

class TestForm(Form):
    answers = fields.RadioField(label='Answer: ')
    confirm = fields.SubmitField(label='Save')
"""
from flask_wtf import Form
from wtforms import fields

from .ciphers import Ciphers, Modes


__all__ = (
    'DeencryptForm',
)


class DeencryptForm(Form):
    key = fields.StringField(label='Key: ')
    mode = fields.RadioField(label='Mode: ', choices=Modes.choices())
    cipher = fields.RadioField(label='Cipher: ', choices=Ciphers.choices())
    decrypt = fields.BooleanField(label='Decrypt (inverse direction)')
    file_name = fields.FileField(label='File name: ')
    raw_text = fields.TextAreaField(label='Raw content: ')
    confirm = fields.SubmitField(label='Process')
