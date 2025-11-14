# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

class Solution:    
    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        

        def merge2Lists(list1, list2):
            
            dummy = ListNode()
            list3 = dummy

            while list1 and list2:

                if list1.val <= list2.val:
                    list3.next = list1
                    list1 = list1.next
                else:
                    list3.next = list2
                    list2 = list2.next
                list3 = list3.next

            list3.next = list1 if list1 else list2

            return dummy.next


        q = lists

        while len(q) > 1:
            l1, l2 = q.pop(0), q.pop(0)
            q.append(merge2Lists(l1, l2))

        if q:
            return q.pop()



