class Node:
    def __init__(self,id, name):
        self.id = id
        self.name = name
        self.next = None



def insert(head,id, name):
    new_head = Node(id,name)
    new_head.next = head
    return new_head


def print_node(head):
    while head:
        print head.id, head.name
        head = head.next
    return

