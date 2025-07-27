from collections import deque, Counter

class Solution:
    def leastInterval(self, tasks, n):
        import heapq
        from collections import deque
        max_heap = [-1*i for i in Counter(tasks).values()]
        heapq.heapify(max_heap)
        q = deque()
        time = 0
        while max_heap or q:
            time += 1
            if max_heap:
                cnt = 1 + heapq.heappop(max_heap)
                if cnt:
                    q.append((cnt, time+n))
            if q and q[0][-1] == time:
                heapq.heappush(max_heap, q.popleft()[0])
        return time

tasks = ["A","A","A","A","A","A","B","C","D","E","F","G"]
n = 2
s = Solution()
out = s.leastInterval(tasks, n)
print(out)