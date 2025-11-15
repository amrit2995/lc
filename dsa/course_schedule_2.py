class Solution:
    def findOrder(self, numCourses: int, prerequisites: List[List[int]]) -> List[int]:
        prereq = {c:[] for c in range(numCourses)}
        out = []
        for crs in prerequisites:
            prereq[crs[0]].append(crs[1])

        visit, visiting = set(), set()

        def dfs(crs):
            if crs in visiting:
                return False
            if crs in visit:
                return True
            visiting.add(crs)
            for pre in prereq[crs]:
                if not dfs(pre):
                    return False
            visiting.remove(crs)
            visit.add(crs)
            out.append(crs)
            return True

        for crs in prereq:
            if not dfs(crs):
                return []
        return out