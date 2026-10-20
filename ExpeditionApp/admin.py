from django.contrib import admin
from .models import Expedition
from django.utils import timezone
from django.contrib import admin
from .models import Expedition


from django.contrib import admin
from .models import Expedition


class FiltrePrix(admin.SimpleListFilter):
    title = "Prix"
    parameter_name = "prix_max"

    def lookups(self, request, model_admin):
        return [
            ("100", "Inférieur à 100"),
            ("1000", "Inférieur à 1 000"),
            ("10000", "Inférieur à 10 000"),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                prix__lt=int(self.value())
            )
        return queryset


class EnRetardFilter(admin.SimpleListFilter):
 title = 'en retard'
 parameter_name = 'en_retard'
 def lookups(self, request, model_admin):
    return [('oui', 'Oui'), ('non', 'Non')]
 def queryset(self, request, queryset):
    if self.value() == 'oui':
        return queryset.filter(statut='publiee',date_souhaitee__lt=timezone.now().date())
    if self.value() == 'non':
        return queryset.exclude(statut='publiee',date_souhaitee__lt=timezone.now().date())
    return queryset
@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'ville_depart', 'ville_arrivee', 'poids_kg', 'date_souhaitee', 'statut', 'entreprise')
    list_filter = ('statut', 'ville_depart',EnRetardFilter,FiltrePrix,)
    search_fields = ('reference', 'entreprise_raison_sociale')
