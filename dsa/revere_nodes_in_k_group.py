from typing import Optional
# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:

        def get_kth(curr, k):
            """Return the kth node from curr (inclusive of curr.next), or None if fewer than k nodes remain."""
            while curr and k > 0:
                curr = curr.next
                k -= 1
            return curr

        def reverse_ll(start, end):
            """
            Reverse the linked list starting at `start` up to (but not including) `end`.
            Returns the new head (end of reversed group).
            """
            prev, curr = end, start
            while curr != end:
                tmp = curr.next
                curr.next = prev
                prev = curr
                curr = tmp
            return prev   # new head of reversed segment

        dummy = ListNode(0, head)
        groupPrev = dummy

        while True:
            kth = get_kth(groupPrev, k)
            if not kth:  # fewer than k nodes left
                break

            groupNext = kth.next
            start = groupPrev.next  # start of the current group

            # reverse the group
            new_head = reverse_ll(start, groupNext)

            # connect previous group to new head
            groupPrev.next = new_head
            groupPrev = start  # move to end of the reversed group for next iteration

        return dummy.next
