from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone

# Validators
matricule_fiscal_validator = RegexValidator(
    regex=r'^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$',
    message="Format attendu : 7 chiffres, 1 lettre (clé de contrôle), "
            "1 lettre (A/B/D/N/P), 1 lettre (M/P/C/N/E), 3 chiffres "
            "(ex. 1234567AAM000 ou 1234567-A-A-M-000)."
)

user_id_validator = RegexValidator(
    regex=r'^\d{2}user\d{2}$',
    message="Le format attendu pour user_id est AAuserNN (ex. 26user00)."
)


def validate_email(value):
    if not value:
        raise ValidationError("L'adresse e-mail est obligatoire.")
    domain = value.rsplit('@', 1)[-1].lower() if '@' in value else ''
    if domain != 'gmail.com':
        raise ValidationError("Seuls les emails appartenant au domaine gmail.com sont acceptés.")


class Utilisateur(AbstractUser):
    user_id = models.CharField(
        max_length=8,
        primary_key=True,
        editable=False,
        validators=[user_id_validator]
    )
    email = models.EmailField(
        unique=True,
        validators=[validate_email]
    )
    telephone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('chargeur', 'Chargeur'),
            ('transporteur', 'Transporteur'),
            ('administrateur', 'Administrateur'),
        ],
        default='chargeur'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.email:
            validate_email(self.email)

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = self._generate_user_id()
        if not self.username:
            self.username = self.user_id
        if not self.password:
            self.set_unusable_password()
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def _generate_user_id(cls):
        annee = timezone.now().strftime('%y')
        prefixe = f"{annee}user"

        dernier = (
            cls.objects
            .filter(user_id__startswith=prefixe)
            .order_by('-user_id')
            .first()
        )
        compteur = int(dernier.user_id[-2:]) + 1 if dernier else 0

        if compteur > 99:
            raise ValidationError(
                f"Limite de 100 utilisateurs atteinte pour l'année 20{annee}."
            )

        return f"{prefixe}{compteur:02d}"

    def __str__(self):
        return f"{self.user_id} ({self.email})"


class Entreprise(models.Model):
    class TypeEntreprise(models.TextChoices):
        CHARGEUR = 'chargeur', 'Chargeur'
        TRANSPORTEUR = 'transporteur', 'Transporteur'

    raison_sociale = models.CharField(max_length=200)
    matricule_fiscal = models.CharField(
        max_length=17,
        unique=True,
        validators=[matricule_fiscal_validator]
    )
    adresse = models.TextField(
        validators=[
            MinLengthValidator(20, "L'adresse ne peut pas comporter moins de 20 caractères."),
            MaxLengthValidator(400, "L'adresse ne peut pas dépasser 400 caractères.")
        ]
    )
    type_entreprise = models.CharField(
        max_length=20,
        choices=TypeEntreprise.choices
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    gerant = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='entreprise'
    )

    # Propriétés de rétrocompatibilité
    @property
    def matricules_fiscale(self):
        return self.matricule_fiscal

    @matricules_fiscale.setter
    def matricules_fiscale(self, value):
        self.matricule_fiscal = value

    @property
    def raison_social(self):
        return self.raison_sociale

    @raison_social.setter
    def raison_social(self, value):
        self.raison_sociale = value

    def clean(self):
        super().clean()
        if self.adresse and len(self.adresse.strip()) < 20:
            raise ValidationError({
                'adresse': "L'adresse doit comporter au moins 20 caractères."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.raison_sociale} ({self.get_type_entreprise_display()})"
