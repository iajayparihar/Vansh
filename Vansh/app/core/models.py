from django.db import models
from django.contrib.auth.models import User

class FamilyMember(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=30, verbose_name='First Name')
    last_name = models.CharField(max_length=30, verbose_name='Last Name')
    date_of_birth = models.DateField(verbose_name='Date of Birth')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Gender')
    address = models.TextField(null=True, blank=True, verbose_name='Address')
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name='Phone Number')
    email = models.EmailField(null=True, blank=True, verbose_name='Email')
    occupation = models.CharField(max_length=50, null=True, blank=True, verbose_name='Occupation')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Relationship(models.Model):
    RELATIONSHIP_CHOICES = [
        ('parent', 'Parent'),
        ('child', 'Child'),
        ('spouse', 'Spouse'),
        ('sibling', 'Sibling'),
        ('uncle', 'Uncle'),
        ('aunt', 'Aunt'),
        ('bua', 'Bua'),
        ('fufaji', 'Fufaji'),
        ('cousin', 'Cousin'),
        ('grandparent', 'Grandparent'),
        ('grandchild', 'Grandchild'),
        ('nephew', 'Nephew'),
        ('niece', 'Niece'),
        # Add more relationship types as needed
    ]

    RELATIONSHIP_REVERSE = {
        'parent': 'child',
        'child': 'parent',
        'spouse': 'spouse',
        'sibling': 'sibling',
        'uncle': 'nephew',  
        'aunt': 'niece',
        'bua': 'nephew',    
        'fufaji': 'niece',
        'cousin': 'cousin',
        'grandparent': 'grandchild',
        'grandchild': 'grandparent',
        'nephew': 'uncle',
        'niece': 'aunt',
    }

    from_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name='from_relationships')
    to_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name='to_relationships')
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, verbose_name='Relationship Type')
    is_spouse = models.BooleanField(default=False, verbose_name='Is Spouse')

    class Meta:
        unique_together = ('from_member', 'to_member', 'relationship_type')
        verbose_name = 'Family Relationship'
        verbose_name_plural = 'Family Relationships'

    def __str__(self):
        return f'{self.from_member} is {self.relationship_type} of {self.to_member}'

