import random
from faker import Faker
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import FamilyMember, Relationship

fake = Faker()

class Command(BaseCommand):
    help = 'Generate a large family tree with mock data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generating family members...')
        family_members = self.generate_family_members(100)
        self.stdout.write('Generating relationships...')
        self.generate_relationships(family_members)
        self.stdout.write(self.style.SUCCESS('Successfully generated family tree.'))

    def generate_family_members(self, count):
        family_members = []
        for _ in range(count):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password=fake.password(),
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            member = FamilyMember.objects.create(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                date_of_birth=fake.date_of_birth(minimum_age=0, maximum_age=100),
                gender=random.choice(['M', 'F', 'O']),
                address=fake.address(),
                phone_number=fake.phone_number(),
                email=user.email,
                occupation=fake.job()
            )
            family_members.append(member)
        return family_members

    def generate_relationships(self, family_members):
        for i in range(len(family_members) - 1):
            from_member = family_members[i]
            to_member = family_members[i + 1]
            Relationship.objects.create(
                from_member=from_member,
                to_member=to_member,
                relationship_type=random.choice(['parent', 'spouse', 'sibling', 'uncle', 'aunt', 'bua', 'fufaji', 'cousin', 'grandparent', 'nephew', 'niece'])
            )
