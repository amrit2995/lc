class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        
        
        def horizontal_bsearch(start, end, blist, target):
            
            mid = (end+start)//2
            if start > end:
                return False
            elif blist[mid] > target:
                return horizontal_bsearch(start, mid-1, blist, target)
            elif blist[mid] < target:
                return horizontal_bsearch(mid+1, end, blist, target)
            else:
                return True

        def vertical_bsearch(start, end, matrix, target):
            
            mid = (end+start)//2
            if start > end:
                return False
            elif matrix[mid][0] > target:
                return vertical_bsearch(start, mid-1, matrix, target)

            elif matrix[mid][-1] < target:
                return vertical_bsearch(mid+1, end, matrix, target)
            else:
                return matrix[mid]

        
        blist = vertical_bsearch(0, len(matrix)-1, matrix, target)
        if not blist:
            return False

        return horizontal_bsearch(0, len(blist)-1, blist, target)
