from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Relationship

@receiver(post_save, sender=Relationship)
def create_reverse_relationship(sender, instance, created, **kwargs):
    if created:
        reverse_type = Relationship.RELATIONSHIP_REVERSE.get(instance.relationship_type)
        if reverse_type:
            Relationship.objects.get_or_create(
                from_member=instance.to_member,
                to_member=instance.from_member,
                relationship_type=reverse_type
            )
