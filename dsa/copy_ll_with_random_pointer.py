"""
# Definition for a Node.
class Node:
    def __init__(self, x: int, next: 'Node' = None, random: 'Node' = None):
        self.val = int(x)
        self.next = next
        self.random = random
"""

class Solution:
    def copyRandomList(self, head: 'Optional[Node]') -> 'Optional[Node]':

        copy_map = collections.defaultdict(lambda: Node(0))
        copy_map[None] = None

        curr = head

        while curr:
            copy_map[curr].val = curr.val
            copy_map[curr].next = copy_map[curr.next]
            copy_map[curr].random = copy_map[curr.random]
            curr = curr.next
        return copy_map[head]