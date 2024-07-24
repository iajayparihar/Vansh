from django.shortcuts import render

from django.http import HttpResponse
from .models import FamilyMember, Relationship
from graphviz import Digraph

def family_tree_view(request):
    dot = Digraph(comment='Family Tree')

    # Add family members as nodes
    family_members = FamilyMember.objects.all()
    for member in family_members:
        dot.node(str(member.id), f"{member.first_name} {member.last_name}")

    # Add relationships as edges
    relationships = Relationship.objects.all()
    for relationship in relationships:
        from_id = relationship.from_member.id
        to_id = relationship.to_member.id
        relationship_type = relationship.relationship_type
        dot.edge(str(from_id), str(to_id), label=relationship_type)

    # Render the graph as SVG
    svg = dot.pipe(format='svg').decode('utf-8')

    return HttpResponse(svg, content_type='image/svg+xml')
