from django.shortcuts import render
from .models import FamilyMember, Relationship
from .schemas import FamilyTreeSchema
from django.http import JsonResponse
import graphviz


#This function builds a doubly linked list of family members based on the relationships.
class FamilyTreeNode:
    def __init__(self, member):
        self.member = member
        self.parents = []
        self.children = []
        self.spouses = []
        self.next = None
        self.prev = None

def build_family_tree():
    relationships = Relationship.objects.all()
    family_tree = {}
    head = None
    tail = None

    for relationship in relationships:
        from_id = relationship.from_member.id
        to_id = relationship.to_member.id

        if from_id not in family_tree:
            family_tree[from_id] = FamilyTreeNode(relationship.from_member)
            if tail:
                tail.next = family_tree[from_id]
                family_tree[from_id].prev = tail
                tail = family_tree[from_id]
            else:
                head = tail = family_tree[from_id]

        if to_id not in family_tree:
            family_tree[to_id] = FamilyTreeNode(relationship.to_member)
            if tail:
                tail.next = family_tree[to_id]
                family_tree[to_id].prev = tail
                tail = family_tree[to_id]
            else:
                head = tail = family_tree[to_id]

        if relationship.relationship_type == 'parent':
            family_tree[to_id].parents.append(family_tree[from_id])
            family_tree[from_id].children.append(family_tree[to_id])
        elif relationship.relationship_type == 'spouse':
            family_tree[from_id].spouses.append(family_tree[to_id])
            family_tree[to_id].spouses.append(family_tree[from_id])

    return head


#This function generates a Graphviz graph from the family tree linked list.
def generate_family_tree_graph(family_tree, relevant_ids):
    dot = graphviz.Digraph(comment='Family Tree')
    added_nodes = set()
    current = family_tree

    while current:
        member = current.member
        member_id = member.id
        member_name = f"{member.first_name} {member.last_name}"

        if member_id not in relevant_ids:
            current = current.next
            continue

        if member_id not in added_nodes:
            dot.node(str(member_id), member_name)
            added_nodes.add(member_id)

        for parent in current.parents:
            parent_id = parent.member.id
            parent_name = f"{parent.member.first_name} {parent.member.last_name}"
            if parent_id in relevant_ids and parent_id not in added_nodes:
                dot.node(str(parent_id), parent_name)
                added_nodes.add(parent_id)
            dot.edge(str(parent_id), str(member_id), label="parent")

        for child in current.children:
            child_id = child.member.id
            child_name = f"{child.member.first_name} {child.member.last_name}"
            if child_id in relevant_ids and child_id not in added_nodes:
                dot.node(str(child_id), child_name)
                added_nodes.add(child_id)
            dot.edge(str(member_id), str(child_id), label="child")

        if current.spouses:
            with dot.subgraph() as s:
                s.attr(rank='same')
                for spouse in current.spouses:
                    spouse_id = spouse.member.id
                    spouse_name = f"{spouse.member.first_name} {spouse.member.last_name}"
                    if spouse_id in relevant_ids and spouse_id not in added_nodes:
                        s.node(str(spouse_id), spouse_name)
                        added_nodes.add(spouse_id)
                    s.edge(str(member_id), str(spouse_id), label="spouse")

        current = current.next

    return dot


#This function retrieves the family data for a specific user from the linked list.
def get_user_family_data(user_id, head):
    current = head
    user_data = None

    while current:
        if current.member.id == user_id:
            user_data = current
            break
        current = current.next

    if not user_data:
        return {'error': 'User not found'}

    response_data = {
        'user': {
            'id': user_data.member.id,
            'first_name': user_data.member.first_name,
            'last_name': user_data.member.last_name,
            'date_of_birth': user_data.member.date_of_birth,
            'gender': user_data.member.gender,
            'address': user_data.member.address,
            'phone_number': user_data.member.phone_number,
            'email': user_data.member.email,
            'occupation': user_data.member.occupation
        },
        'spouse': None,
        'children': [],
        'siblings': [],
        'parents': []  # Include parents in the response data
    }

    if user_data.spouses:
        spouse = user_data.spouses[0]
        response_data['spouse'] = {
            'id': spouse.member.id,
            'first_name': spouse.member.first_name,
            'last_name': spouse.member.last_name,
            'date_of_birth': spouse.member.date_of_birth,
            'gender': spouse.member.gender,
            'address': spouse.member.address,
            'phone_number': spouse.member.phone_number,
            'email': spouse.member.email,
            'occupation': spouse.member.occupation
        }

    for child in user_data.children:
        response_data['children'].append({
            'id': child.member.id,
            'first_name': child.member.first_name,
            'last_name': child.member.last_name,
            'date_of_birth': child.member.date_of_birth,
            'gender': child.member.gender,
            'address': child.member.address,
            'phone_number': child.member.phone_number,
            'email': child.member.email,
            'occupation': child.member.occupation
        })

    for parent in user_data.parents:
        response_data['parents'].append({
            'id': parent.member.id,
            'first_name': parent.member.first_name,
            'last_name': parent.member.last_name,
            'date_of_birth': parent.member.date_of_birth,
            'gender': parent.member.gender,
            'address': parent.member.address,
            'phone_number': parent.member.phone_number,
            'email': parent.member.email,
            'occupation': parent.member.occupation
        })
        siblings = parent.children
        for sibling in siblings:
            if sibling.member.id != user_id:
                response_data['siblings'].append({
                    'id': sibling.member.id,
                    'first_name': sibling.member.first_name,
                    'last_name': sibling.member.last_name,
                    'date_of_birth': sibling.member.date_of_birth,
                    'gender': sibling.member.gender,
                    'address': sibling.member.address,
                    'phone_number': sibling.member.phone_number,
                    'email': sibling.member.email,
                    'occupation': sibling.member.occupation
                })

    return response_data


#This function handles the request and generates the family tree for a specific user.
def user_family_view(request, user_id):
    head = build_family_tree()
    family_data = get_user_family_data(user_id, head)
    if 'error' in family_data:
        return JsonResponse(family_data, safe=False)

    relevant_ids = {user_id}

    if 'spouse' in family_data and family_data['spouse']:
        relevant_ids.add(family_data['spouse']['id'])
        spouse_data = get_user_family_data(family_data['spouse']['id'], head)
        for sibling in spouse_data['siblings']:
            relevant_ids.add(sibling['id'])

    for child in family_data['children']:
        relevant_ids.add(child['id'])

    for sibling in family_data['siblings']:
        relevant_ids.add(sibling['id'])

    for parent in family_data['parents']:
        relevant_ids.add(parent['id'])

    dot = generate_family_tree_graph(head, relevant_ids)
    graph_path = 'family_tree_user'
    dot.render(graph_path, format='png', cleanup=True)

    return JsonResponse({'family_data': family_data, 'graph_path': graph_path}, safe=False)


def family_tree_view(request):
    head = build_family_tree()
    current = head
    family_tree = {}
    while current:
        family_tree[current.member.id] = current
        current = current.next

    family_tree_schema = FamilyTreeSchema(many=True)
    family_tree_data = family_tree_schema.dump([v for v in family_tree.values()])

    dot = generate_family_tree_graph(head, {member_id for member_id in family_tree.keys()})
    graph_path = 'family_tree01'
    dot.render(graph_path, format='png', cleanup=True)

    return JsonResponse({'family_tree_data': family_tree_data, 'graph_path': graph_path}, safe=False)
