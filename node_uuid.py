import uuid 

class Node():
    def __init__(self, parent=None, content=[], id=None):
        self.parent = parent
        self.id = str(uuid.uuid4()) if id is None else id
        self.content = content
        self.children = []
        if self.parent:
            self.parent.appendChild(self)

    def appendChild(self, child):
        self.children.append(child)
    
    def toList(self):
        return [self.id, self.content]

    def getChildren(self):
        return self.children
    
    def getParent(self):
        return self.parent

    def removeChild(self, child):
        self.children.remove(child)

    def removeChildren(self):
        self.children = []

    def childrenCount(self):
        return len(self.children)

    def getId(self):
        return self.id

if __name__ == '__main__':
    root = Node(None, ['column', 'comment'])
    parent1 = Node(root, ['AAA', 'aaa'])
    parent2 = Node(root, ['BBB', 'bbb'])
    child1 = Node(parent1, ['CCC', 'ccc'])