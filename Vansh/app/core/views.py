from django.shortcuts import render
from .models import FamilyMember, Relationship
from .schemas import FamilyTreeSchema
from django.http import JsonResponse

def build_family_tree():
    # Fetch all relationships
    relationships = Relationship.objects.all()

    # Build a dictionary to hold the tree
    family_tree = {}

    # Populate relationships
    for relationship in relationships:
        if relationship.to_member.id not in family_tree:
            family_tree[relationship.to_member.id] = {
                'member': relationship.to_member,
                'parents': [],
                'children': [],
                'spouses': []
            }
        if relationship.from_member.id not in family_tree:
            family_tree[relationship.from_member.id] = {
                'member': relationship.from_member,
                'parents': [],
                'children': [],
                'spouses': []
            }

        # Handle parent and child relationships
        if relationship.relationship_type == 'parent':
            family_tree[relationship.to_member.id]['parents'].append(relationship.from_member)
            family_tree[relationship.from_member.id]['children'].append(relationship.to_member)

        # Handle spouse relationships
        elif relationship.relationship_type == 'spouse':
            # Ensure no duplicate entries
            if relationship.to_member not in family_tree[relationship.from_member.id]['spouses']:
                family_tree[relationship.from_member.id]['spouses'].append(relationship.to_member)
            if relationship.from_member not in family_tree[relationship.to_member.id]['spouses']:
                family_tree[relationship.to_member.id]['spouses'].append(relationship.from_member)

    # Return the family tree dictionary
    return family_tree

def family_tree_view(request):
    family_tree = build_family_tree()
    family_tree_schema = FamilyTreeSchema(many=True)
    family_tree_data = family_tree_schema.dump(family_tree.values())
    return JsonResponse(family_tree_data, safe=False)