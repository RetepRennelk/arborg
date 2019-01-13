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
        child.parent = self
    
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

    def moveChildUp(self, idx):
        if idx > 0:
            self.children[idx], self.children[idx-1] = self.children[idx-1], self.children[idx]
            return True
        return False

    def insertChild(self, child, idx):
        self.children.insert(idx, child)
        child.parent = self

    def makeChildrenToGrandChildren(self, pivotChild):
        '''All siblings below pivotChild will be reparented to pivotChild.
        '''
        idx = self.children.index(pivotChild)
        N_children = self.childrenCount()
        for _ in range(idx+1, N_children):
            child = self.children[idx+1]
            self.removeChild(child)
            pivotChild.appendChild(child)
    
    def makeChildrenToSiblings(self):
        '''All children will be reparented to parent below this item.
        '''
        idx = self.parent.children.index(self)
        N_children = self.childrenCount()
        for i in range(N_children):
            child = self.children[0]
            self.removeChild(child)
            self.parent.insertChild(child, idx+i+1)
    
if __name__ == '__main__':
    if 1:
        root = Node(None, ['column', 'comment'])
        parent1 = Node(root, ['AAA', 'aaa'])
        parent2 = Node(root, ['BBB', 'bbb'])
        child1 = Node(parent2, ['CCC', 'ccc'])
        child2 = Node(parent2, ['DDD', 'ddd'])

        parent2.makeChildrenToSiblings()

    else:
        root = Node(None, ['column', 'comment'])
        parent1 = Node(root, ['AAA', 'aaa'])
        parent2 = Node(root, ['BBB', 'bbb'])
        parent3 = Node(root, ['CCC', 'ccc'])
        parent4 = Node(root, ['DDD', 'ddd'])

        root.makeChildrenToGrandChildren(parent2)
    print(root)