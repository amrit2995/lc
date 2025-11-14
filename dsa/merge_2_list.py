# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        
        final = None
        first = list1
        second = list2
        dummy = head = ListNode()

        while first and second:
            
            if first.val <= second.val:
                head.next = first
                first = first.next
            elif second:
                head.next = second
                second = second.next
            head = head.next

        head.next = first or second
        return dummy.next