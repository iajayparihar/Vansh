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

def generate_family_tree_graph(family_tree, user_id=None):
    dot = graphviz.Digraph(comment='Family Tree')

    # Track added nodes to avoid duplication
    added_nodes = set()

    # Add nodes and edges to the graph
    for member_id, data in family_tree.items():
        if user_id is not None and member_id != user_id:
            continue

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
        if user_id is not None and member_id != user_id:
            continue

        if data['spouses']:
            with dot.subgraph() as s:
                s.attr(rank='same')
                for spouse in data['spouses']:
                    s.node(str(spouse.id), f"{spouse.first_name} {spouse.last_name}")
                    s.edge(str(member_id), str(spouse.id))

    return dot

def get_user_family_data(user_id, family_tree):
    # Initialize the response data
    response_data = {
        'user': None,
        'spouse': None,
        'children': [],
        'siblings': []
    }

    if user_id not in family_tree:
        return {'error': 'User not found'}

    user_data = family_tree[user_id]
    user = user_data['member']
    response_data['user'] = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'date_of_birth': user.date_of_birth,
        'gender': user.gender,
        'address': user.address,
        'phone_number': user.phone_number,
        'email': user.email,
        'occupation': user.occupation
    }

    # Fetch the user's spouse
    if user_data['spouses']:
        spouse = user_data['spouses'][0]  # Assuming one spouse
        response_data['spouse'] = {
            'id': spouse.id,
            'first_name': spouse.first_name,
            'last_name': spouse.last_name,
            'date_of_birth': spouse.date_of_birth,
            'gender': spouse.gender,
            'address': spouse.address,
            'phone_number': spouse.phone_number,
            'email': spouse.email,
            'occupation': spouse.occupation
        }

    # Fetch the user's children
    for child in user_data['children']:
        response_data['children'].append({
            'id': child.id,
            'first_name': child.first_name,
            'last_name': child.last_name,
            'date_of_birth': child.date_of_birth,
            'gender': child.gender,
            'address': child.address,
            'phone_number': child.phone_number,
            'email': child.email,
            'occupation': child.occupation
        })

    # Fetch the user's siblings
    for parent in user_data['parents']:
        siblings = family_tree[parent.id]['children']
        for sibling in siblings:
            if sibling.id != user.id:
                response_data['siblings'].append({
                    'id': sibling.id,
                    'first_name': sibling.first_name,
                    'last_name': sibling.last_name,
                    'date_of_birth': sibling.date_of_birth,
                    'gender': sibling.gender,
                    'address': sibling.address,
                    'phone_number': sibling.phone_number,
                    'email': sibling.email,
                    'occupation': sibling.occupation
                })

    return response_data

def user_family_view(request, user_id):
    family_tree = build_family_tree()
    family_data = get_user_family_data(user_id, family_tree)
    if 'error' in family_data:
        return JsonResponse(family_data, safe=False)

    # Generate Graphviz family tree for the specific user and their relatives
    relevant_ids = {user_id}
    
    # Add the user's spouse to the relevant IDs
    if 'spouse' in family_data and family_data['spouse']:
        relevant_ids.add(family_data['spouse']['id'])
        # Add the spouse's siblings to the relevant IDs
        spouse_data = get_user_family_data(family_data['spouse']['id'], family_tree)
        for sibling in spouse_data['siblings']:
            relevant_ids.add(sibling['id'])

    # Add the user's children to the relevant IDs
    for child in family_data['children']:
        relevant_ids.add(child['id'])

    # Add the user's siblings to the relevant IDs
    for sibling in family_data['siblings']:
        relevant_ids.add(sibling['id'])

    # Generate a sub-tree containing only the relevant family members
    sub_tree = {k: v for k, v in family_tree.items() if k in relevant_ids}

    dot = generate_family_tree_graph(sub_tree, user_id=user_id)
    graph_path = 'family_tree_user'
    dot.render(graph_path, format='png', cleanup=True)

    return JsonResponse({'family_data': family_data, 'graph_path': graph_path}, safe=False)


def family_tree_view(request):
    family_tree = build_family_tree()
    family_tree_schema = FamilyTreeSchema(many=True)
    family_tree_data = family_tree_schema.dump(family_tree.values())

    # Generate Graphviz family tree
    dot = generate_family_tree_graph(family_tree)
    graph_path = 'family_tree01'
    dot.render(graph_path, format='png', cleanup=True)

    return JsonResponse({'family_tree_data': family_tree_data, 'graph_path': graph_path}, safe=False)
