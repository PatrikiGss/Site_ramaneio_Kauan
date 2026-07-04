from django import forms

from .models import Carga


class CargaForm(forms.ModelForm):
    class Meta:
        model = Carga
        fields = ['tipo_maca', 'tamanho', 'quantidade_caixas', 'peso_total', 'observacoes']
        widgets = {
            'tipo_maca': forms.Select(attrs={'class': 'form-select'}),
            'tamanho': forms.Select(attrs={'class': 'form-select'}),
            'quantidade_caixas': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 1, 'inputmode': 'numeric',
            }),
            'peso_total': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 0.01, 'step': '0.01', 'inputmode': 'decimal',
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Informações adicionais sobre a carga (opcional)',
            }),
        }

    def clean_quantidade_caixas(self):
        quantidade = self.cleaned_data['quantidade_caixas']
        if quantidade < 1:
            raise forms.ValidationError('A quantidade de caixas deve ser no mínimo 1.')
        return quantidade

    def clean_peso_total(self):
        peso = self.cleaned_data['peso_total']
        if peso <= 0:
            raise forms.ValidationError('O peso total deve ser maior que zero.')
        return peso


class FiltroCargaForm(forms.Form):
    busca = forms.CharField(
        required=False,
        label='Busca',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar nas observações ou nº da carga...',
        }),
    )
    tipo_maca = forms.ChoiceField(
        required=False,
        label='Tipo da maçã',
        choices=[('', 'Todos os tipos')] + list(Carga.TipoMaca.choices),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    tamanho = forms.ChoiceField(
        required=False,
        label='Tamanho',
        choices=[('', 'Todos os tamanhos')] + list(Carga.Tamanho.choices),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    data_inicio = forms.DateField(
        required=False,
        label='De',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    data_fim = forms.DateField(
        required=False,
        label='Até',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
