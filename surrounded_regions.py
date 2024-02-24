class Solution:
    def solve(self, board):
        """
        Do not return anything, modify board in-place instead.
        """
        
        def dfs(r, c):
            if board[r][c] != "O":
                return 

            board[r][c] = "E"
            all_d = ((-1, 0),(1,0),(0,-1),(0,1))

            for dr,dc in all_d:
                nr,nc = r+dr,c+dc
                if nr in range(len(board)) and nc in range(len(board[0])):
                    dfs(nr,nc)

        for i in range(len(board)):
            for j in range(len(board[0])):
                if i not in range(1, len(board)-1) or j not in range(1, len(board[0])-1):
                    dfs(i,j)
        
        print(board)
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == "O":
                    board[i][j] = "X"
                elif board[i][j] == "E":
                    board[i][j] = "O"
        return board
    
    
s = Solution()
board = [["X","O","X"],["O","X","O"],["X","O","X"]]
ans = s.solve(board)
print(ans)