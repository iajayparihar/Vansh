from django.shortcuts import render
from .models import FamilyMember, Relationship

def build_family_tree():
    # Fetch all family members and relationships
    family_members = FamilyMember.objects.all()
    relationships = Relationship.objects.all()

    # Build a dictionary to hold the tree
    family_tree = {}
    # Initialize the dictionary with all family members
    for member in family_members:
        family_tree[member.id] = {
            'member': member,
            'parents': [],
            'children': [],
            'spouses': []
        }

    # Populate relationships
    for relationship in relationships:
        if relationship.relationship_type == 'parent':
            family_tree[relationship.to_member.id]['parents'].append(family_tree[relationship.from_member.id])
            family_tree[relationship.from_member.id]['children'].append(family_tree[relationship.to_member.id])
        elif relationship.relationship_type == 'spouse':
            family_tree[relationship.from_member.id]['spouses'].append(family_tree[relationship.to_member.id])
            family_tree[relationship.to_member.id]['spouses'].append(family_tree[relationship.from_member.id])

    # Return the family tree dictionary
    return family_tree

def family_tree_view(request):
    family_tree = build_family_tree()
    print(family_tree)
    return render(request, 'index.html', {'family_tree': family_tree})
