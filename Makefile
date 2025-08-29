# Makefile for RPAL interpreter in Python

# Default input file
INPUT=input.rpal

# Run normally
run:
	python myrpal.py $(INPUT)

# Run with -ast switch
ast:
	python myrpal.py -ast $(INPUT)


