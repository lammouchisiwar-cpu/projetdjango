from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
# Create your models here.
class Utilisateur(AbstractUser):
    user_id=models.CharField(primary_key=True,max_length=8)
    email=models.EmailField(unique=True)
    telephone=models.CharField(max_length=15,blank=True,null=True)
    role=models.CharField(max_length=20,choices=[
        ('admin','Admin'),
        ('c','Chargeur'),
        ('t','Transporteur') 
        ],default='c')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class Entreprise(models.Model):
    raison_social=models.CharField(max_length=200,blank=False, null=False)
    matricules_fiscale=models.CharField(max_length=17,unique=True)
    adresse=models.TextField(validators=[MinLengthValidator(20,"l'adresse ne peut pas avoir moins de 20 char"),MaxiLengthValidator(400,"l'adresse ne peut pas depasser les 400 char")])
    type_entreprise=models.CharField(max_length=100,choices=[
        ('c','Chargeur'),
        ('t','Transporteur')
    ])
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    gerant=models.OneToOneField(Utilisateur,on_delete=models.CASCADE,related_name='entreprise')
