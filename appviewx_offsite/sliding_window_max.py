class Solution:
    def maxSlidingWindow(self, nums, k):
        import heapq
        heap = []
        ans = []
        visited = {}
        for r in range(len(nums)):
            visited[nums[r]] = visited.get(nums[r], 0) + 1
            heapq.heappush(heap,-nums[r])

            if r-k+1 >=0:
                ans.append(-heap[0])

                visited[nums[r-k+1]] -= 1
                if visited[nums[r-k+1]] <= 0:
                    visited.pop(nums[r-k+1])
                
                while heap and -heap[0] not in visited:
                    heapq.heappop(heap)
        return ans

nums = [1,-1]
k = 1
s =  Solution()
out = s.maxSlidingWindow(nums, k)
print(out)