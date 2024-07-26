from django.shortcuts import render
from .models import FamilyMember, Relationship
from .schemas import FamilyTreeSchema
from django.http import JsonResponse
import graphviz

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

def generate_family_tree_graph(family_tree):
    dot = graphviz.Digraph(comment='Family Tree')

    # Track added nodes to avoid duplication
    added_nodes = set()

    # Add nodes and edges to the graph
    for member_id, data in family_tree.items():
        member_name = f"{data['member'].first_name} {data['member'].last_name}"
        
        if member_id not in added_nodes:
            dot.node(str(member_id), member_name)
            added_nodes.add(member_id)

        for parent in data['parents']:
            if parent.id not in added_nodes:
                dot.node(str(parent.id), f"{parent.first_name} {parent.last_name}")
                added_nodes.add(parent.id)
            dot.edge(str(parent.id), str(member_id), label="parent")

        for child in data['children']:
            if child.id not in added_nodes:
                dot.node(str(child.id), f"{child.first_name} {child.last_name}")
                added_nodes.add(child.id)
            dot.edge(str(member_id), str(child.id), label="child")

    # Add spouses in a subgraph to align them horizontally
    for member_id, data in family_tree.items():
        if data['spouses']:
            with dot.subgraph() as s:
                s.attr(rank='same')
                for spouse in data['spouses']:
                    s.node(str(spouse.id), f"{spouse.first_name} {spouse.last_name}")
                    s.edge(str(member_id), str(spouse.id), label="spouse", dir="none")

    return dot

def family_tree_view(request):
    family_tree = build_family_tree()
    family_tree_schema = FamilyTreeSchema(many=True)
    family_tree_data = family_tree_schema.dump(family_tree.values())

    # Generate Graphviz family tree
    dot = generate_family_tree_graph(family_tree)
    graph_path = 'family_tree.gv'
    dot.render(graph_path, format='png', cleanup=True)

    return JsonResponse({'family_tree_data': family_tree_data, 'graph_path': graph_path}, safe=False)
