class Solution:
    def searchMatrix(self, matrix, target):
        start = 0
        end = len(matrix)

        while start<end:
            mid = (start+end)//2
            if target < matrix[mid][0]:
                end = mid
            elif target > matrix[mid][-1]:
                start = mid+1
            else:
                break

        row = matrix[mid]
        start = 0
        end = len(row)

        while start < end:
            mid = (start+end)//2
            
            if target < row[mid]:
                end = mid
            elif target > row[mid]:
                start = mid+1
            else:
                return True
        return False


matrix =  [[1,3,5,7],[10,11,16,20],[23,30,34,60]]
target = 16
matrix =  [[1,3]]
target = 3

s = Solution()
print(s.searchMatrix(matrix, target))