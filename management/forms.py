from django import forms


class ConfigForm(forms.Form):
    allow_new_order = forms.BooleanField(label='Allow New Order', required=False)
    allow_update_order = forms.BooleanField(label='Allow Update Order', required=False)
    allow_delete_order = forms.BooleanField(label='Allow Delete Order', required=False)
