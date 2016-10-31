.PHONY: all clean

all: rapport

rapport: rapport.tex
	pdflatex rapport.tex

clean:
	rm -rf *~ *.pyc
