from game import DiGraph
from copy import deepcopy

edge_weight = 1
blob_score = 10

def graph(x, y, max_depth):
        # Make a graph on the go
        G = DiGraph()
        root = G.newNode((x, y), 0)
        parents = [root]
        children = []
        for i in range(1, max_depth):
            y_temp = y + 4*i
            for x_temp in range(x-i, x+i+1):
                if (x_temp < 0 or x_temp > 12):
                    continue
                new_node = G.newNode((x_temp, y_temp), weight = 0)
                children.append(new_node)
            for parent in parents:
                for child in children:
                    if (abs(child.data[0] - parent.data[0]) <= 1):
                        if (child.isLeftNode(parent)):
                            parent.addEdge(child, -edge_weight)
                            child.setParent(parent, edge_weight)
                        elif(child.isRightNode(parent)):
                            parent.addEdge(child, edge_weight)
                            child.setParent(parent, -edge_weight)
                        else:
                            parent.addEdge(child, 0)
                            child.setParent(parent, 0)
            print(parents)
            print(children)
            print("\n")
            parents = children         
            children = []
        return G
                        
def main():
    G = graph(5, 0, 7)
    print(G.link_count)
    print(G.node_count)
    # for node in G.nodes:
        # print(node.data)
    
if __name__ == '__main__':
    main()
    