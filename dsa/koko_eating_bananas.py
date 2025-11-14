from typing import List
class Solution:
    def minEatingSpeed(self, piles: List[int], h: int) -> int:
        
        import math
        start, end = 1, max(piles)
        mid = 0


        while start <= end:

            mid = (start+end)//2
            
            hours = sum([math.ceil(p/mid) for p in piles ])

            if hours > h:
                start = mid + 1
            else:
                end = mid - 1
            
        return start


            
