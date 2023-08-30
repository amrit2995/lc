class Solution:
    def solve(self, board):
        """
        Do not return anything, modify board in-place instead.
        """
        def dfs(r,c):

            if (r,c) in not_replaceable:
                return True

            if (r,c) in visited:
                return False

            visited.add((r,c))

            if board[r][c] == "X":
                return False

            if r not in range(1,len(board)-1) or c not in range(1,len(board[0])-1):
                not_replaceable.add((r,c))
                return True

            dir = [(-1,0),(1,0),(0,-1),(0,1)]

            not_replace = []

            for dr,dc in dir:
                nr,nc = r+dr, c+dc

                if nr in range(len(board)) and nc in range(len(board[0])):
                    not_replace.append(dfs(nr,nc))
            if any(not_replace):
                not_replaceable.add((r,c))
                return True
            board[r][c] = "X"
            return False

        visited = set()
        not_replaceable = set()
        for i in range(len(board)):
            for j in range(len(board[0])):
                dfs(i,j)
            
                    

board = [
    ["O","O","O","O","X","X"],
    ["O","O","O","O","O","O"],
    ["O","X","O",   "X","O","O"],
    ["O","X","O","O","X","O"],
    ["O","X","O","X","O","O"],
    ["O","X","O","O","O","O"]]
s = Solution()
out = s.solve(board)
print(board)
