from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone


reference_validator = RegexValidator(
    regex=r'^EXP-\d{2}-\d{5}$',
    message="La structure doit suivre le format EXP-AA-NNNNN."
)


class Expedition(models.Model):
    class Statut(models.TextChoices):
        PUBLIEE = 'publiee', 'Publiée'
        ATTRIBUEE = 'attribuee', 'Attribuée'
        EN_COURS = 'en_cours', 'En cours'
        LIVREE = 'livree', 'Livrée'
        ANNULEE = 'annulee', 'Annulée'

    reference = models.CharField(
        max_length=32,
        unique=True,
        editable=False,
        validators=[reference_validator]
    )
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    poids_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), "Le poids doit être strictement supérieur à 0 kg.")]
    )
    date_souhaitee = models.DateField()
    description = models.TextField(blank=True)
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.PUBLIEE
    )

    entreprise = models.ForeignKey(
        'EntrepriseApp.Entreprise',
        on_delete=models.CASCADE,
        related_name='expeditions',
        limit_choices_to={'type_entreprise': 'chargeur'}
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reference} ({self.ville_depart} -> {self.ville_arrivee})"

    def clean(self):
        super().clean()
        if self.poids_kg is not None and self.poids_kg <= 0:
            raise ValidationError({
                'poids_kg': "Ne pas accepter un poids nul."
            })
        if self.entreprise_id and self.entreprise.type_entreprise != 'chargeur':
            raise ValidationError({
                'entreprise': "Une expédition ne peut être créée que par une entreprise de type chargeur."
            })

    @classmethod
    def _generate_reference(cls):
        annee = timezone.now().strftime('%y')
        prefixe = f"EXP-{annee}-"
        dernier = (
            cls.objects
            .filter(reference__startswith=prefixe)
            .order_by('-reference')
            .first()
        )
        compteur = int(dernier.reference[-5:]) + 1 if dernier else 1
        if compteur > 99999:
            raise ValidationError(
                f"Limite de 99999 expéditions atteinte pour l'année 20{annee}."
            )
        return f"{prefixe}{compteur:05d}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        self.full_clean()
        super().save(*args, **kwargs)
