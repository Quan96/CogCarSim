import sys
import heapq
from game import Actions

class Node:
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

class PriorityQueue():
    def __init__(self):
        self.container = []
        self.count = 0
        
    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.container, entry)
        self.count += 1
        
    def pop(self):
        (_,_,item) = heapq.heappop(self.container)
        return item

    def isEmpty(self):
        return len(self.container) == 0
    
    def update(self, item, priority):
        """
        * If item already in priority queue with higher priority, update its priority and rebuild the heap.
        * If item already in priority queue with equal or lower priority, do nothing.
        * If item not in priority queue, do the same thing as self.push.
        """
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.container[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.container)
                break
        else:
            self.push(item, priority)
            
def aStarSearch(problem, heuristic):
    actions=PriorityQueue()
    locations=PriorityQueue()
    startLocation=problem.getStartState()
    # (location, actions, cost)
    startNode = (startLocation, [], 0)
    actions.push(startNode, 0)
    locations.push([startLocation], 0)
    visited=set()
    
    while not actions.isEmpty():
        currentNode=actions.pop()
        location = locations.pop()
        if problem.isGoalState(currentNode[0]):
            # print location
            return currentNode[1], location
        if currentNode[0] not in visited:
            visited.add(currentNode[0])
            for successor in problem.getSuccessors(currentNode[0]):
                if successor[0] not in visited:
                    cost = currentNode[2] + successor[2]
                    totalCost = cost + heuristic(successor[0], problem)
                    actions.push( (successor[0], currentNode[1]+[successor[1]], cost), totalCost )
                    locations.push( location + [successor[0]], totalCost )
                    
    return None

# class MonteCarloTreeSearch(object):
    
        
def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

class SearchProblem:
    def getStartState(self):
        raise NotImplemented
    
    def isGoalState(self, state):
        raise NotImplemented
    
    def getSuccessors(self, state):
        raise NotImplemented
    
    def getCostOfActions(self, actions):
        raise NotImplemented

class ShortestPathProblem(SearchProblem):
    def __init__(self, costFn = lambda x: 1, goal=(12095, 0), start=None):
        self.startState = (0, 6) # the center of the start
        if start != None: self.startState=start
        self.goal = goal
        self.costFn = costFn
        
        # For display purposes
        self._visited, self._visitedlist, self._expanded = {}, [], 0
        
    def getStartState(self):
        return self.startState
    
    def isGoalState(self, state):
        isGoal = state == self.goal
        
        if isGoal:
            self._visitedlist.append(state)
            
        return isGoal
    
    def getSuccessors(self, state):
        successors = []
        for action in [Actions.LEFT, Actions.RIGHT, Actions.STRAIGHT]:
            y, x = state
            dy, dx = Actions.directionToVector(action)  #modified
            nextY, nextX = int(y + dy), int(x + dx)
            if nextX < 0:
                nextState = (nextY, 0)
            elif nextX > 12:
                nextState = (nextY, 12)
            else:
                nextState = (nextY, nextX)
            cost = self.costFn(nextState)
            successors.append( (nextState, action, cost) )
                
        self._expanded += 1
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)
            
        return successors
    
    # def getCostOfActions(self, actions):
    #     # if actions == None: return 999999
    #     y, x = self.getStartState()
    #     cost = 0
    #     for action in actions:
    #         dy, dx = Actions.directionToVector(action)
    #         y, x = int(y + dy), int(x + dx)
    #         cost += self.costFn( (y, x) )
    #     return cost
    
def manhattanHeuristic(position, problem):
    xy1 = position
    xy2 = problem.goal
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])

class SafestPathProblem(SearchProblem):
    def __init__(self, costFn, goal=(12095, 0), start=None):
        self.startState = (0, 6) # the center of the start
        if start != None: self.startState = start
        self.goal = goal
        self.costFn = costFn
        
        # For display purpose
        self._visited, self._visitedlist, self._expanded = {}, [], 0
        
    def getStartState(self):
        return self.startState
    
    def isGoalState(self, state):
        isGoal = state == self.goal
        
        if isGoal:
            self._visitedlist.append(state)
            
        return isGoal
    
    def getSuccessors(self, state):
        successors = []
        for action in [Actions.LEFT, Actions.RIGHT, Actions.STRAIGHT]:
            y, x = state
            dy, dx = Actions.directionToVector(action)  #modified
            nextY, nextX = int(y + dy), int(x + dx)
            if nextX < 0:
                nextState = (nextY, 0)
            elif nextX > 12:
                nextState = (nextY, 12)
            else:
                nextState = (nextY, nextX)
            cost = self.costFn(nextState)
            successors.append( (nextState, action, cost) )
                
        self._expanded += 1
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)
            
        return successors