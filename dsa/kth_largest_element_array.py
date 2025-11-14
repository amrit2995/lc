class Solution:
    def findKthLargest(self, nums: List[int], k: int) -> int:
        
        heap = []
        heapq.heapify(heap)

        for n in nums:
            if len(heap) < k:
                heapq.heappush(heap, n)
            elif heap[0] <= n:
                heapq.heappop(heap)
                heapq.heappush(heap, n)
            # print(heap[0], heap)
        return heapq.heappop(heap)