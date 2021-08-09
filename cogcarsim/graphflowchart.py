from pyflowchart import *

# st = StartNode('Init a root node')
# cond = ConditionNode('State is found in search tree')
# op = OperationNode('Expand the graph')
# io = InputOutputNode(InputOutputNode.OUTPUT, 'The game graph')
# cond2 = ConditionNode('The node not at egde')
# op2 = OperationNode('Expand 2 child nodes')
# op3 = OperationNode('Expand 3 child nodes')
# cond3 = ConditionNode('Max depth reached')
# e = EndNode('The graph stop expanding')

st = StartNode("Selection")
cond = ConditionNode("State is found in search tree")
cond_true = OperationNode("Using UCB to select child node")
op = OperationNode("Expansion")

io = InputOutputNode(InputOutputNode.OUTPUT, "Next action for the car")
op2 = OperationNode("Simulation")
op3 = OperationNode("Backpropagation")


# define the direction the connection will leave the node from
st.connect(cond)
cond.connect_yes(op)
cond.connect_no(e)
op.connect(cond2)
cond2.connect_yes(op3)
cond2.connect_no(op2)
op2.connect(cond3)
op3.connect(cond3)
cond3.connect_yes(io)
cond3.connect_no(op)

fc = Flowchart(st)
print(fc.flowchart())
