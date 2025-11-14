class Solution:
    def lastStoneWeight(self, stones: List[int]) -> int:

        import heapq

        heap = [-s for s in stones]
        heapq.heapify(heap)

        while len(heap)>1:
            x, y = heapq.heappop(heap), heapq.heappop(heap)
            z = -abs(y-x)
            heapq.heappush(heap, z)
        return -heapq.heappop(heap)