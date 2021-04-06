all:
	hfst-lexc nahuat/lexc/variant.lexc -o nahuat/fst/input.hfst
	hfst-lexc nahuat/lexc/dico.lexc -o nahuat/fst/dico.hfst
	hfst-lexc nahuat/lexc/flex_orth.lexc -o nahuat/fst/flex.hfst
	hfst-lexc nahuat/lexc/vln.lexc -o nahuat/fst/vln.hfst
	hfst-lexc nahuat/lexc/isoglosses.lexc -o nahuat/fst/isoglosses.hfst

	hfst-union -1 nahuat/fst/flex.hfst -2 nahuat/fst/vln.hfst -o nahuat/fst/flex_vln.hfst
	hfst-union -1 nahuat/fst/flex.hfst -2 nahuat/fst/isoglosses.hfst -o nahuat/fst/flex_isoglosses.hfst
	hfst-union -1 nahuat/fst/vln.hfst -2 nahuat/fst/isoglosses.hfst -o nahuat/fst/vln_isoglosses.hfst
	hfst-union -1 nahuat/fst/flex_isoglosses.hfst -2 nahuat/fst/vln.hfst -o nahuat/fst/flex_isoglosses_vln.hfst


	hfst-compose -1 nahuat/fst/input.hfst -2 nahuat/fst/flex.hfst -o nahuat/fst/in2dic_flex.hfst
	hfst-compose -1 nahuat/fst/input.hfst -2 nahuat/fst/vln.hfst -o nahuat/fst/in2dic_vln.hfst
	hfst-compose -1 nahuat/fst/input.hfst -2 nahuat/fst/isoglosses.hfst -o nahuat/fst/in2dic_isoglosses.hfst
	hfst-compose -1 nahuat/fst/input.hfst -2 nahuat/fst/flex_vln.hfst -o nahuat/fst/in2dic_flex_vln.hfst
	hfst-compose -1 nahuat/fst/input.hfst -2 nahuat/fst/flex_isoglosses.hfst -o nahuat/fst/in2dic_flex_isoglosses.hfst
	hfst-compose -1 nahuat/fst/input.hfst -2 nahuat/fst/vln_isoglosses.hfst -o nahuat/fst/in2dic_vln_isoglosses.hfst
	hfst-compose -1 nahuat/fst/input.hfst -2 nahuat/fst/flex_isoglosses_vln.hfst -o nahuat/fst/in2dic_flex_isoglosses_vln.hfst

clean:
	rm nahuat/fst/*.hfst
