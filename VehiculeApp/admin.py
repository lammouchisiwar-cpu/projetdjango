from django.contrib import admin
from .models import Vehicule


@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'entreprise', 'type_vehicule', 'capacite_kg', 'disponible')
    list_filter = ('disponible', 'type_vehicule')
    search_fields = ('immatriculation', 'entreprise__raison_sociale')  # requis par l'autocomplete d'Offre
    list_editable = ('disponible',)       # édition rapide demandée au bloc 1
    ordering = ('entreprise', 'immatriculation')
    autocomplete_fields = ('entreprise',)  # bloc 2 : FK en champ de recherche
    list_per_page = 25