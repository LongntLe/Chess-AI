# Chess-AI

## ANALYSIS

### Design

The chess engine is built upon python-chess, thus saving times to actually implement the minimax algorithm and its related features, such as a database for storing moves, alpha-beta pruning, and various evaluation functions.

The design of the chess engine is built upon: https://medium.freecodecamp.org/simple-chess-ai-step-by-step-1d55a9266977, with extensive modifications based on additional info retrieved from chessprogramming.com.

### AI behaviors

Due to the many evaluation functions implementated, the AI displays "sane" behaviors in its choice as to which move to take. For example, the AI would prioritize a domination of the center, as center pieces are evaluated higher in the evaluation matrices. However, the AI would also prioritizes getting a "number advantage" whenever possible, as pieces are valued much higher than positions. In short, the AI would refrain from making "foolish" moves and might prove to be a competitive player against some beginners/ lower-intermediate players as it makes careful moves that avert a losing state in a reasonable amount of time.

Checkmate would, of course, being the ultimate goal of the AI. Thus the very high value associated with it. An arbitrary value is assigned to a simple check as the wikipedia page on chessprogramming does not mention this evaluation. This values would be subject to further revisions if deemed necessary.

Technology-speaking, I aim to maximize the layers of depth the AI could traverse without taking an inconvenient amount of time (from a human's perspective). Currently, the AI is able to traverse around 4 layers at max before things get uncomfortable. 

### Critiques

The AI is rather predictable as it does not react well with any other opening strategies rather than the classic e4/d5 opening. This is because the evaluation matrices are static and reflect only that opening.

The AI might also not be able to display fancy sacrificial moves as such approaches requires thinking many moves ahead. In this case, the search tree depth limit that a regular laptop could withstand is an obstacle. The database does help in speeding up the search time in some cases, but this heuristic would prove to be trivial as we reach further depth levels.

I would also imagine the AI performs badly with closing moves, when players are left with a few pieces with quite a wide range of movements (i.e a Rook and a King vs a Bishop and a King), as this simply requires traversing a deeper search tree to find an elegant approach.

The AI relies on static piece value. This is impractical in some cases. For example, a single bishop remaining on the board should have a lower evaluation as a bishop is incapable of reaching half of the board. Two bishops are strong, and a single one is not. Also, a knight would tend to be valued higher in the beginning of the game as it could reach behind the enemy's pawn structure with ease. As the game reaches a close, knights are not as important as there are more spaces for pieces to move freely.

Lastly, as much as the AI would try to conserve its pieces, it might not be as careful to develop a strong, long-term well-defensed army. Such a task would require either 1/ traversing a deeper search tree to prevent any attacks on an isolated piece to happen or 2/ another evaluation heuristic that prioritizes piece structure.

### Potential Expansions

From the critiques above, I propose a few ways the AI could be improved:

1/ Implement more evaluation functions. A few candidates are: pawn structures, piece structures, isolated pawns, dynamic evaluation functions.

2/ Implement moves and counter moves for classic states. For example, counter-moves regarding different opening strategies, and different approaches to close the game given certain pieces on board. (E.g. if the game state is simply a Rook + a King vs a King, the game could be closed in a standard approach without relying on any searching algorithm.)

3/ Deepen the depth of the search tree. This might include implementing a better search technique (for example, iterative deepning), move ordering (as to prevent the worse case of minimax, when moves are order strictly ascending for a maximizer, or descending for a minimizer, from happening), or optimizing using low-level languages such as C.

4/ Better organize the repo for further modularization and refactorization. But it is not the priority currently.

### Insights

It seems that the evaluation functions in this case complement the minimax algorithm well as it makes up for the depth limit of the search tree by heuristics that enhances the quality of the decision making process.
