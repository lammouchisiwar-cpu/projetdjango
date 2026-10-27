# from django.contrib import admin, messages
# from django.core.exceptions import ValidationError
# from django.utils import timezone
# from django.utils.html import format_html
# from OffreApp.models import Offre
# from .models import Expedition

# STATUT_CLOTURE = 'livree'   

# class FiltrePrix(admin.SimpleListFilter):
#     title = "Prix"
#     parameter_name = "prix_max"

#     def lookups(self, request, model_admin):
#         return [
#             ("100", "Inférieur à 100"),
#             ("1000", "Inférieur à 1 000"),
#             ("10000", "Inférieur à 10 000"),
#         ]

#     def queryset(self, request, queryset):
#         if self.value():
#             return queryset.filter(
#                 prix__lt=int(self.value())
#             )
#         return queryset
# class EnRetardFilter(admin.SimpleListFilter):
#     title = 'en retard'
#     parameter_name = 'en_retard'

#     def lookups(self, request, model_admin):
#         return [('oui', 'Oui'), ('non', 'Non')]

#     def queryset(self, request, queryset):
#         aujourdhui = timezone.now().date()
#         if self.value() == 'oui':
#             return queryset.filter(statut='publiee', date_souhaitee__lt=aujourdhui)
#         if self.value() == 'non':
#             return queryset.exclude(statut='publiee', date_souhaitee__lt=aujourdhui)
#         return queryset

# class OffreInline(admin.StackedInline):
#     model = Offre
#     fk_name = 'expedition'
#     extra = 0
#     can_delete = False
#     show_change_link = True
#     readonly_fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')

#     def has_add_permission(self, request, obj=None):
#         return False   

# @admin.action(description='Clôturer les expéditions sélectionnées')
# def cloturer_expeditions(modeladmin, request, queryset):
#     cloturees, ignorees, erreurs = 0, 0, 0
#     for exp in queryset:
#         if exp.statut != 'en_cours':
#             ignorees += 1
#             continue
#             exp.statut = STATUT_CLOTURE
#         try:
#             exp.full_clean()
#             exp.save()                    
#             cloturees += 1
#         except ValidationError as e:
#             erreurs += 1
#             modeladmin.message_user(
#                 request, f'{exp.reference} : {"; ".join(e.messages)}', level=messages.ERROR)

#         if cloturees:
#             modeladmin.message_user(request, f'{cloturees} expédition(s) clôturée(s).', messages.SUCCESS)
#         if ignorees:
#             modeladmin.message_user(
#                 request, f'{ignorees} expédition(s) ignorée(s) (statut différent de « en cours »).',
#                 messages.WARNING,)
# @admin.register(Expedition)
# class ExpeditionAdmin(admin.ModelAdmin):
#     list_display = ('reference', 'entreprise', 'ville_depart', 'ville_arrivee',
#                     'statut', 'statut_colore', 'date_souhaitee')
#     list_display_links = ('reference',)
#     list_filter = ('statut', 'ville_depart', EnRetardFilter)
#     search_fields = ('reference', 'entreprise__raison_sociale')   # requis par l'autocomplete d'Offre
#     list_editable = ('statut',)
#     ordering = ('-created_at',)
#     date_hierarchy = 'date_souhaitee'
#     list_per_page = 25
#     autocomplete_fields = ('entreprise',)
#     readonly_fields = ('reference', 'created_at', 'updated_at', 'statut_colore')
#     inlines = [OffreInline]
#     actions = [cloturer_expeditions]

#     fieldsets = (
#         ('Informations générales', {'fields': ('reference', 'entreprise')}),
#         ('Trajet', {'fields': ('ville_depart', 'ville_arrivee', 'date_souhaitee', 'poids_kg', 'description')}),
#         ('Suivi', {'fields': ('statut', 'statut_colore', 'created_at', 'updated_at')}),
#     )

# @admin.display(description='Badge', ordering='statut')
# def statut_colore(self, obj):
#     couleurs = {
#         'brouillon': '#777777', 'publiee': '#F0AD4E', 'attribuee': '#5BC0DE',
#         'en_cours': '#337AB7', 'livree': '#5CB85C', 'annulee': '#D9534F',
#     }
#     return format_html(
#         '<span style="color:white;background:{};padding:3px 8px;border-radius:4px;">{}</span>',
#         couleurs.get(obj.statut, '#999'), obj.get_statut_display(),
#     )