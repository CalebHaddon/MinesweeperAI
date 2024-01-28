import itertools
import random

#from Minesweeper.runner import HEIGHT, WIDTH
HEIGHT = 8
WIDTH = 8

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        if len(self.cells) == self.count:
            return self.cells
        return None


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return None
        
    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        
        if cell in self.cells:
            print("sentence edited in mark_mine:")
            print("before:")
            print(self.cells)
            print(self.count)
            self.cells.discard(cell)
            self.count -= 1 
            print("after")
            print(self.cells)
            print(self.count)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        
        if cell in self.cells:
            print("sentence edited in mark_safe:")
            print("before:")
            print(self.cells)
            print(self.count)
            self.cells.discard(cell)
            print("after")
            print(self.cells)
            print(self.count)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """

        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """

        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        self.moves_made.add(cell)
        self.mark_safe(cell)
        k = cell[0]
        d = cell[1]
        added_from_subset = []
        adjacent_cells = self.get_adjacent(k, d)
        print("added from adjacent:")
        print(adjacent_cells, count)
        count -= adjacent_cells[1]
        self.knowledge.append(Sentence(adjacent_cells[0], count))
        changed = True
        while changed == True:
            changed = False
            print("thinking")

            for sentence in self.knowledge:
                if len(sentence.cells) != 0:

                    subtracted = 0
                    for y in range(len(sentence.cells)):
                        y -= subtracted
                        temp = list(sentence.cells)
                        if temp[y] in self.moves_made:
                            changed = True
                            sentence.cells.discard(temp[y])
                            subtracted += 1

                    if sentence.count == 0:
                        changed = True
                        subtracted = 0
                        for i in range(len(sentence.cells)):
                            i -= subtracted
                            safecell = list(sentence.cells)[i]
                            self.mark_safe(safecell)
                            subtracted += 1

                    if len(sentence.cells) == sentence.count and len(sentence.cells) != 0:
                        changed = True
                        subtracted = 0
                        for o in range(len(sentence.cells)):
                            o -= subtracted
                            self.mark_mine(list(sentence.cells)[o])
                            subtracted += 1

                    for sentence1 in self.knowledge:
                        if sentence.cells.issubset(sentence1.cells) and sentence.cells != sentence1.cells and len(sentence.cells) != 0:
                            changed = True
                            new_sentence = (set(),0)
                            editable = list(new_sentence)
                            editable[0] = sentence1.cells - sentence.cells
                            editable[1] = sentence1.count - sentence.count
                            new_sentence = editable
                            same = False
                            for sentence2 in self.knowledge:
                                if new_sentence[0] == sentence2.cells:
                                    same = True
                                    changed = False
                            if same  == False:
                                added_from_subset.append((new_sentence[0], new_sentence[1]))
                                print("added from subset:")
                                print(added_from_subset)
                                self.knowledge.append(Sentence(new_sentence[0], new_sentence[1]))
            
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        iterable = list(self.safes)
        for i in range(len(self.safes)):
            if iterable[i] not in self.moves_made and iterable[i] not in self.mines:
                print("safe move")
                print(iterable[i])
                return iterable[i]
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        count = 0
        while True:
            count += 1
            i = random.randrange(HEIGHT)
            j = random.randrange(WIDTH)
            move = (i,j)
            if move not in self.moves_made:
                if move not in self.mines:
                    #allmines = Sentence.known_mines(self)
                    #print("known_mines")
                    #print(allmines)
                    print("random move:")
                    print(move)
                    return move
            if count == 200:
                return None
            
    def get_adjacent(self, k, d):
        adjacent_count = 0
        adjacent = list()
        i = k
        j = d
        subtract = False
        subtracted = 0
        adjacent.append((i-1, j-1))
        adjacent.append((i-1, j))
        adjacent.append((i-1, j+1))
        adjacent.append((i, j-1))
        adjacent.append((i, j+1))
        adjacent.append((i+1, j-1))
        adjacent.append((i+1, j))
        adjacent.append((i+1, j+1))
        subtracting = 0
        for i in range(8):
            i -= subtracting
            if adjacent[i] in self.mines:
                adjacent.remove(adjacent[i])
                adjacent_count += 1
                subtracting += 1
            elif adjacent[i] in self.safes:
                adjacent.remove(adjacent[i])
                subtracting += 1
        
        subtracted = 0
        for u in range(len(adjacent)):
            u -= subtracted
            if adjacent[u][0] >= HEIGHT or adjacent[u][0] < 0:
                adjacent.remove(adjacent[u])
                subtracted += 1
            elif adjacent[u][1] >= WIDTH or adjacent[u][1] < 0:
                adjacent.remove(adjacent[u])
                subtracted += 1
        
        return (adjacent, adjacent_count)
