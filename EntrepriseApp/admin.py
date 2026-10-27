# #from django.contrib import admin
# #from VehiculeApp.models import Vehicule
# #from .models import Entreprise
# #from django.contrib.auth.admin import UserAdmin
# #from django.contrib.auth.forms import UserChangeForm, UserCreationForm
# from .models import Utilisateur

# class UtilisateurCreationForm(UserCreationForm):
#     class Meta(UserCreationForm.Meta):
#         model = Utilisateur
#         fields = ('username', 'email', 'first_name', 'last_name', 'role')


# class UtilisateurChangeForm(UserChangeForm):
#     class Meta(UserChangeForm.Meta):
#         model = Utilisateur
#         fields = '__all__'


# @admin.register(Utilisateur)
# class UtilisateurAdmin(UserAdmin):
#     add_form = UtilisateurCreationForm
#     form = UtilisateurChangeForm
#     model = Utilisateur

#     list_display = ('user_id', 'username', 'email', 'role', 'is_staff', 'is_active')
#     list_filter = ('role', 'is_staff', 'is_active')
#     search_fields = ('user_id', 'username', 'email', 'first_name', 'last_name')
#     ordering = ('-created_at',)
#     readonly_fields = ('user_id', 'last_login', 'date_joined', 'created_at', 'updated_at')

#     fieldsets = (
#         ('Identité', {'fields': ('user_id', 'username', 'password')}),
#         ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email')}),
#         ('Rôle et permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser',
#                                             'groups', 'user_permissions')}),
#         ('Suivi', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
#     )
#     add_fieldsets = (
#         (None, {'classes': ('wide',),
#                 'fields': ('username', 'email', 'first_name', 'last_name', 'role',
#                            'password1', 'password2')}),
#     )
# class VehiculeInline(admin.TabularInline):
#     model = Vehicule
#     extra = 0                     
#     fields = ('immatriculation', 'type_vehicule', 'capacite_kg', 'disponible')


# @admin.register(Entreprise)
# class EntrepriseAdmin(admin.ModelAdmin):
#     list_display = ('raison_sociale', 'matricule_fiscal', 'type_entreprise','utilisateur')
#     list_filter = ('type_entreprise',)
#     search_fields = ('raison_sociale', 'matricule_fiscal','utilisateur_email')  
#     autocomplete_fields=['utilisateur']
#     ordering = ('raison_sociale',)
#     list_per_page = 25
#     inlines = [VehiculeInline]
#     readonly_fields = ('created_at', 'updated_at')          
#     fieldsets = (
#         ('Identité', {'fields': ('raison_sociale', 'matricule_fiscal', 'type_entreprise')}),
#         ('Suivi', {'fields': ('created_at', 'updated_at')}),
#         ('contact',{'fields':('adresse','utilisateur')}),
#     )#