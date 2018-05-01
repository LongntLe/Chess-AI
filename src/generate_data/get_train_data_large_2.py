"""
This file reads the pgn files one game at a time to 
store the X, y arrays into npz files. 
Its much more suitable for large data which cannot 
fit into memory all at once.

Adapt from: Ashudeep Singh
"""
import numpy as np
import pgn
import chess
#import cPickle as npy
import copy
from util import *
import sys, os
import timeit
import argparse
parser=argparse.ArgumentParser\
	(description='Convert PGN data into numpy arrays of size 6*8*8 with labels (pieces/moves)')
parser.add_argument('--dir', type=str, default='', help='The data directory')
parser.add_argument('--odir', type=str, default='', help='The output hdf5 data directory')
parser.add_argument('-v', dest='verbose', action='store_true')
parser.add_argument('--minelo', type=int, default=2000, 
	help='Minimum ELO rating to be added to training data')
parser.add_argument('--elo', dest='elo_layer', action='store_true',
	help='Whether to include ELO rating layer or not')
parser.add_argument('--C', type=float, default=1255, 
	help='Divide the ELO rating minus Min ELO rating by this value')
parser.add_argument('--partsize', type=int, default=2500, 
	help='Number of games to be dumped into 1 npz file.')
parser.add_argument('--multi', dest='multiple_layers', action='store_true',
	help='Use multiple layers for a single piece to get (8,8,12) size \
	image per board. Default: False.')
parser.add_argument('--piecelayer', dest='piece_layer', action='store_true',
	help='Append a layer with the piece being played marked as 1 for the move\
	network data.')
parser.set_defaults(verbose=False)
parser.set_defaults(elo_layer=False)
parser.set_defaults(multiple_layers=False)
parser.set_defaults(piece_layer=False)
args = parser.parse_args()

if args.elo_layer:
	elo_layer = True
else:
	elo_layer = False

min_elo = args.minelo
PGN_DATA_DIR = args.dir
TRAIN_DATA_DIR = args.odir
if not os.path.isdir(TRAIN_DATA_DIR):
	os.mkdir(os.getcwd()+"/"+TRAIN_DATA_DIR)

NUM_GAMES = 2500

#assign the correct functions from util.py
if args.multiple_layers:
	bitboard_to_image = convert_bitboard_to_image_2
	flip_color = flip_color_2
else:
	bitboard_to_image = convert_bitboard_to_image_1
	flip_color = flip_color_1

print "Started reading PGN files in directory %s"%PGN_DATA_DIR
game_index = 0
for f in os.listdir(PGN_DATA_DIR):
	if ".pgn" in f:
		print "%s file opened...."%f
		for game in pgn.GameIterator(PGN_DATA_DIR+"/"+f):
			if not game:	break
			#print PGN_DATA_DIR+"/"+f, game
			board = chess.Bitboard()
			moves = game.moves
			if game_index%NUM_GAMES == 0:
				if game_index!=0:
					end = timeit.default_timer()
					print "Processed %d moves from %d games in %fs"%(len(X), NUM_GAMES,end-start)
					start = timeit.default_timer()
					print "Saving data for %d-%d games.."%(game_index-NUM_GAMES,game_index)

					print "Saving X array..."
					output = TRAIN_DATA_DIR+'/X_%d_%d.npz' % (game_index-NUM_GAMES,game_index)
					X = np.array(X).astype(np.float32)
					np.savez_compressed(output, X)

					print "Saving y array..."
					output = TRAIN_DATA_DIR+'/y_%d_%d.npz' % (game_index-NUM_GAMES,game_index)
					y = np.array(y).astype(np.float32)
					np.savez_compressed(output, y)

					for i in xrange(6):
						output_array = "p%d_X" % (i + 1)
						print "Saving %s array..." % output_array
						output_array = eval(output_array)
						output_array = np.array(output_array).astype(np.float32)
						output = TRAIN_DATA_DIR+'/p%d_X_%d_%d.npz' % (i + 1, game_index-NUM_GAMES,game_index) 
						np.savez_compressed(output, output_array)

						output_array = "p%d_y" % (i + 1)
						print "Saving %s array..." % output_array
						output_array = eval(output_array)
						output_array = np.array(output_array).astype(np.float32)
						output = TRAIN_DATA_DIR+'/p%d_y_%d_%d.npz' % (i + 1, game_index-NUM_GAMES,game_index) 
						np.savez_compressed(output, output_array)
					end = timeit.default_timer()
					print "Saved arrays into directory %s in %fs"%(TRAIN_DATA_DIR, end-start)

				#clear the buffers
				start = timeit.default_timer()
				X, y = [], []
				p1_X, p2_X, p3_X = [], [], []
				p4_X, p5_X, p6_X = [], [], []
				p1_y, p2_y, p3_y = [], [], []
				p4_y, p5_y, p6_y = [], [], []
			#increment the game counter
			game_index+=1
			black_elo = int(game.blackelo)
			white_elo = int(game.whiteelo)
			if black_elo < min_elo:
				skip_black = True
			else:
				skip_black = False
			if white_elo < min_elo:
				skip_white = True
			else:
				skip_white = False
			if skip_white and skip_black:	continue
			if elo_layer:
				white_elo_layer = float(white_elo - min_elo)/args.C
				black_elo_layer = float(black_elo- min_elo)/args.C
			for move_index, move in enumerate(moves):
				if move[0].isalpha(): # check if move is SAN
					from_to_chess_coords = board.parse_san(move)
					from_to_chess_coords = str(from_to_chess_coords)

					from_chess_coords = from_to_chess_coords[:2]
					to_chess_coords = from_to_chess_coords[2:4]
					from_coords = chess_coord_to_coord2d(from_chess_coords)
					to_coords = chess_coord_to_coord2d(to_chess_coords)
								
					if move_index % 2 == 0:
						im = bitboard_to_image(board)
						skip = skip_white
						if elo_layer:
							last_layer = white_elo_layer*np.ones((1,8,8))
					else:
						im = flip_image(bitboard_to_image(board))
						im = flip_color(im)
						from_coords = flip_coord2d(from_coords)
						to_coords = flip_coord2d(to_coords)
						skip = skip_black
						if elo_layer:
							last_layer = black_elo_layer*np.ones((1,8,8))

					index_piece = np.where(im[from_coords] == 1)
					# index_piece denotes the index in PIECE_TO_INDEX
					index_piece = index_piece[0][0]/2 # ranges from 0 to 5

					from_coords = flatten_coord2d(from_coords)
					to_coords = flatten_coord2d(to_coords)

					im = np.rollaxis(im, 2, 0) # to get into form (C, H, W)
					
					if elo_layer:
						im = np.append(im, last_layer, axis=0)

					board.push_san(move)

					#don't write if the player<2000 ELO
					if skip:
						continue
					# Filling the X and y array
					X.append(im)
					y.append(from_coords)

					# Filling the p_X and p_y array
					p_X = "p%d_X" % (index_piece + 1)
					p_X = eval(p_X)

					if args.piece_layer:
						piece_layer = np.zeros((1,8,8))
						piece_layer[0, from_coords/8, from_coords%8] = 1
						im = np.append(im, piece_layer,axis=0)
					
					p_X.append(im)

					p_y = "p%d_y" % (index_piece + 1)
					p_y = eval(p_y)
					p_y.append(to_coords)

					end = timeit.default_timer()

print "Processed %d moves from %d games in %fs"%(len(X), game_index%NUM_GAMES,end-start)
start = timeit.default_timer()
print "Saving data for %d-%d games.."%(game_index - game_index%NUM_GAMES,game_index)

print "Saving X array..."
output = TRAIN_DATA_DIR+'/X_%d_%d.npz' % (game_index - game_index%NUM_GAMES,game_index)
X = np.array(X).astype(np.float32)
np.savez_compressed(output, X)

print "Saving y array..."
output = TRAIN_DATA_DIR+'/y_%d_%d.npz' % (game_index - game_index%NUM_GAMES,game_index)
y = np.array(y).astype(np.float32)
np.savez_compressed(output, y)

for i in xrange(6):
	output_array = "p%d_X" % (i + 1)
	print "Saving %s array..." % output_array
	output_array = eval(output_array)
	output_array = np.array(output_array).astype(np.float32)
	output = TRAIN_DATA_DIR+'/p%d_X_%d_%d.npz' % (i + 1, game_index - game_index%NUM_GAMES,game_index) 
	np.savez_compressed(output, output_array)

	output_array = "p%d_y" % (i + 1)
	print "Saving %s array..." % output_array
	output_array = eval(output_array)
	output_array = np.array(output_array).astype(np.float32)
	output = TRAIN_DATA_DIR+'/p%d_y_%d_%d.npz' % (i + 1, game_index - game_index%NUM_GAMES ,game_index) 
	np.savez_compressed(output, output_array)
end = timeit.default_timer()
print "Saved arrays into directory %s in %fs"%(TRAIN_DATA_DIR, end-start)
print "Done with reading %d games"%(game_index+1)