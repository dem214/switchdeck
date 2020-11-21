"""All forms of app `switchdeck`."""
from django import forms

from .models import Comment, Lot, Game


class CommentForm(forms.ModelForm):
    """Form for comments on `Lot` page."""

    class Meta():
        """Metaclass for `CommentForm` class properties."""

        model = Comment
        fields = ['text']


class LotForm(forms.ModelForm):
    """Form to create new `LotFrom`."""

    class Meta():
        """Metaclass for `GLotForm` class properties."""

        model = Lot
        fields = ['game', 'desc', 'prop', 'price']


class LotReducedForm(forms.ModelForm):
    """
    Reduced form for create `Lot`.

    Not include `prop` and `price`
    """

    class Meta():
        """Metaclass for `LotReducedForm` class properties."""

        model = Lot
        fields = ['game', 'desc']


class SetLotForm(forms.ModelForm):
    """Form of `Lot` to set parameters."""

    class Meta():
        """Metaclass for `SetLotForm` class properties."""

        model = Lot
        fields = ['desc', 'price']


class ChangeDescLotForm(forms.ModelForm):
    """Form to change description of `Lot`."""

    class Meta():
        """Metaclass for `ChangeDescLotForm` class properties."""

        model = Lot
        fields = ['desc']


class ChangePriceLotForm(forms.ModelForm):
    """Form to change price of `Lot`."""

    class Meta():
        """Metaclass for `ChangePriceLotForm` class properties."""

        model = Lot
        fields = ['price']


class ChangeToForm(forms.Form):
    """Form contained by available variants of changable `Lots`."""

    changelets = forms.ModelMultipleChoiceField(queryset=None, required=False)

    def __init__(self, *args, instance, **kwargs):
        """Create form and add available variants."""
        super().__init__(*args, **kwargs)
        if instance.prop == 'w' or instance.prop == 'b':
            self.fields['changelets'].queryset = \
                instance.get_change_to_choices()
            self.fields['changelets'].initial = instance.change_to.all()
        elif instance.prop == 'k' or instance.prop == 's':
            self.fields['changelets'].queryset = \
                instance.get_ready_to_change_choices()
            self.fields['changelets'].initial = instance.ready_change_to.all()


class DatalistWidget(forms.TextInput):
    """Widget with dropdown menu of available games."""

    def __init__(self, datalist, name, *args, **kwargs):
        """Initiate widget and fill it with data."""
        super().__init__(*args, **kwargs)
        self._name = name
        self._datalist = datalist
        self.attrs.update({'list': 'list_%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        """Return rendered html text of widget."""
        text_html = super().render(name, value, attrs=attrs)
        datalist = f'<datalist id="list_{self._name}">'
        for item in self._datalist:
            datalist += f'<option value="{item}">'
        datalist += '</datalist>'
        return (text_html + datalist)


class SearchForm(forms.Form):
    """Form from search of `Lots` page."""

    game = forms.CharField(required=False)
    place = forms.CharField(required=False)
    proposition = forms.ChoiceField(choices=(
        ('b', 'buy'),
        ('s', 'sell'),
        ('a', 'all')
    ))

    def __init__(self, *args, **kwargs):
        """Initiate form, fill it with needed widgets."""
        super().__init__(*args, **kwargs)
        list_game = [game.name for game in Game.objects.all()]
        list_game.sort()
        self.fields['game'].widget = DatalistWidget(
            datalist=list_game,
            name='game'
        )
        self.fields['place'].widget = DatalistWidget(
            datalist=[place.name for place in Place.objects.all()],
            name='place'
        )
