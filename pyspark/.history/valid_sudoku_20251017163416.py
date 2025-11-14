from typing import List

class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:

        row_sets = [set() for _ in range(len(board))]
        col_sets = [set() for _ in range(len(board))]
        cell_sets = [[set() for _ in range(len(board[0])//3)] for _ in range(len(board)//3)]

        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] != '.':
                    if board[i][j] in row_sets[i]:
                        return False
                    row_sets[i].add(board[i][j])
                    if board[i][j] in col_sets[j]:
                        return False
                    col_sets[j].add(board[i][j])
                    if board[i][j] in cell_sets[i//3][j//3]:
                        return False
                    cell_sets[i//3][j//3].add(board[i][j])
        return True