"""Lossless exact-decimal SQL projection. This never rounds a source to fit SQL."""
from decimal import Decimal, InvalidOperation

def sql_decimal(text):
    if not isinstance(text,str):raise ValueError('Exact decimal text required')
    try:value=Decimal(text)
    except InvalidOperation:raise ValueError('Invalid decimal')
    if not value.is_finite():raise ValueError('Non-finite decimal')
    canonical=format(value,'f')
    if '.' in canonical:canonical=canonical.rstrip('0').rstrip('.')
    whole,_,fraction=canonical.lstrip('-+').partition('.')
    if len(whole.lstrip('0'))>35 or len(fraction)>30:return None
    return canonical
