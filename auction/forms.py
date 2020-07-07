from django import forms

from .models import Item

class ItemForm(forms.Form):
    title = forms.CharField(required=True)
    description = forms.CharField(required=False)
    price = forms.IntegerField(required=True, min_value=0)
    close_dt = forms.IntegerField(required=True)

    class Meta:
        fields = ('title',
                  'description',
                  'price',
                  'close_dt',
        )


class ItemListForm(forms.Form):
    page = forms.IntegerField(required=False, initial=0)
    page_size = forms.IntegerField(required=False, initial=10)
    sort = forms.CharField(required=False, initial='asc')
    order = forms.CharField(required=False, initial='close_dt')
    search_string = forms.CharField(required=False, initial=None)
    show_closed = forms.BooleanField(required=False, initial=False)

    class Meta:
        fields = ('page',
                  'page_size',
                  'sort',
                  'order',
                  'search_string',
                  'show_closed',
        )

    def clean_page(self):
        if not 'page' in self.data:
            return self.fields['page'].initial
        return self.cleaned_data['page']

    def clean_page_size(self):
        if not 'page_size' in self.data:
            return self.fields['page_size'].initial
        return self.cleaned_data['page_size']     

    def clean_sort(self):
        if not 'sort' in self.data:
            return self.fields['sort'].initial
        return self.cleaned_data['sort']

    def clean_search_string(self):
        if not 'search_string' in self.data:
            return self.fields['search_string'].initial
        return self.cleaned_data['search_string']

    def clean_show_closed(self):
        if not 'show_closed' in self.data:
            return self.fields['show_closed'].initial
        return self.cleaned_data['show_closed']