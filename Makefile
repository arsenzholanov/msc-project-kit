# BasicTeX installs outside the default PATH on macOS.
export PATH := /Library/TeX/texbin:$(PATH)

.PHONY: sweep figures report clean test seeds slides

sweep:
	python3 experiments/rfq/sweep.py --out data/raw

seeds:
	python3 experiments/rfq/seeds.py --out data/raw

figures:
	python3 experiments/rfq/figures.py --data data/raw --out report/figures

test:
	python3 -m pytest experiments/rfq/tests -q

# vancouver.bst emits "et al.." for entries with more than six authors typed as
# @misc; arXiv preprints must be @misc because the style strips the dot from an
# identifier placed in the journal field. The sed fixes the doubled period after
# bibtex and before the final passes. It is deterministic and touches nothing else.
report:
	cd report && pdflatex -interaction=nonstopmode main.tex \
	  && bibtex main \
	  && sed -i '' 's/et~al\.\./et~al./g' main.bbl \
	  && pdflatex -interaction=nonstopmode main.tex \
	  && pdflatex -interaction=nonstopmode main.tex

slides:
	cd slides && pdflatex -interaction=nonstopmode main.tex \
	  && pdflatex -interaction=nonstopmode main.tex

clean:
	cd report && rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot
