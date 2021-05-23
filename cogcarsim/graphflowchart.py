from pyflowchart import *

st = StartNode('Init a root node')
cond = ConditionNode('Max_depth > 2')
op = OperationNode('Expand the graph')
io = InputOutputNode(InputOutputNode.OUTPUT, 'The game graph')
cond2 = ConditionNode('The node not at egde')
op2 = OperationNode('Expand 2 child nodes')
op3 = OperationNode('Expand 3 child nodes')
cond3 = ConditionNode('Max depth reached')
e = EndNode('The graph stop expanding')

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
