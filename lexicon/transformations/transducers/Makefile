all:
	hfst-lexc nahuat/lexc/variant.lexc -o nahuat/fst/input.hfst
	hfst-lexc nahuat/lexc/dico.lexc -o nahuat/fst/to_dico.hfst
	hfst-lexc nahuat/lexc/flex_orth.lexc -o nahuat/fst/flex.hfst
	hfst-lexc nahuat/lexc/vln.lexc -o nahuat/fst/vln.hfst
	hfst-lexc nahuat/lexc/isoglosses.lexc -o nahuat/fst/isoglosses.hfst

	#####################
	# Intermediary FSTs #
	#####################

	# in2flex = input.hfst .o. flex.hfst
	hfst-compose -1 nahuat/fst/input.hfst -2 nahuat/fst/flex.hfst -o nahuat/fst/in2flex.hfst

	# in2vln = input.hfst .o. vln.hfst
	hfst-compose -1 nahuat/fst/input.hfst -2 nahuat/fst/vln.hfst -o nahuat/fst/in2vln.hfst

	# in2iso = input.hfst .o. isoglosses.hfst
	hfst-compose -1 nahuat/fst/input.hfst -2 nahuat/fst/isoglosses.hfst -o nahuat/fst/in2iso.hfst

	# in2flex_iso = in2flex.hfst .o. isoglosses.hfst
	hfst-compose -1 nahuat/fst/in2iso.hfst -2 nahuat/fst/flex.hfst -o nahuat/fst/in2flex_iso.hfst

	# in2flex_vln = vln.hfst .o. in2flex.hfst
	hfst-compose -1 nahuat/fst/in2vln.hfst -2 nahuat/fst/flex.hfst -o nahuat/fst/in2flex_vln.hfst

	# in2vln_iso = in2vln.hfst .o. isoglosses.hfst
	hfst-compose -1 nahuat/fst/in2vln.hfst -2 nahuat/fst/isoglosses.hfst -o nahuat/fst/in2vln_iso.hfst

	# in2flex_vln_iso = in2flex_vln.hfst .o. isoglosses.hfst
	hfst-compose -1 nahuat/fst/in2flex_iso.hfst -2 nahuat/fst/vln.hfst -o nahuat/fst/in2flex_vln_iso.hfst


	###############
	# Output FSTs #
	###############

	# in2dic_flex = in2flex .o. to_dico.hfst
	hfst-compose -1 nahuat/fst/in2flex.hfst -2 nahuat/fst/to_dico.hfst -o nahuat/fst/in2dic_flex.hfst

	# in2dic_vln = in2vln .o. to_dico.hfst
	hfst-compose -1 nahuat/fst/in2vln.hfst -2 nahuat/fst/to_dico.hfst -o nahuat/fst/in2dic_vln.hfst

	# in2dic_iso = in2iso .o. to_dico.hfst
	hfst-compose -1 nahuat/fst/in2iso.hfst -2 nahuat/fst/to_dico.hfst -o nahuat/fst/in2dic_iso.hfst

	# in2dic_flex_vln = in2flex_vln.hfst .o. to_dico.hfst
	hfst-compose -1 nahuat/fst/in2flex_vln.hfst -2 nahuat/fst/to_dico.hfst -o nahuat/fst/in2dic_flex_vln.hfst

	# in2dic_flex_iso = in2flex_iso.hfst .o. to_dico.hfst
	hfst-compose -1 nahuat/fst/in2flex_iso.hfst -2 nahuat/fst/to_dico.hfst -o nahuat/fst/in2dic_flex_iso.hfst

	# in2dic_vln_iso = in2vln_iso.hfst .o. to_dico.hfst
	hfst-compose -1 nahuat/fst/in2vln_iso.hfst -2 nahuat/fst/to_dico.hfst -o nahuat/fst/in2dic_vln_iso.hfst

	# in2dic_flex_vln_iso = in2flex_vln_iso.hfst .o. to_dico.hfst
	hfst-compose -1 nahuat/fst/in2flex_vln_iso.hfst -2 nahuat/fst/to_dico.hfst -o nahuat/fst/in2dic_flex_vln_iso.hfst


	####################
	# Output ATT files #
	####################
	hfst-fst2txt nahuat/fst/in2dic_flex.hfst > nahuat/att/in2dic_flex.att
	hfst-fst2txt nahuat/fst/in2dic_vln.hfst > nahuat/att/in2dic_vln.att
	hfst-fst2txt nahuat/fst/in2dic_iso.hfst > nahuat/att/in2dic_iso.att
	hfst-fst2txt nahuat/fst/in2dic_flex_vln.hfst > nahuat/att/in2dic_flex_vln.att
	hfst-fst2txt nahuat/fst/in2dic_flex_iso.hfst > nahuat/att/in2dic_flex_iso.att
	hfst-fst2txt nahuat/fst/in2dic_vln_iso.hfst > nahuat/att/in2dic_vln_iso.att
	hfst-fst2txt nahuat/fst/in2dic_flex_vln_iso.hfst > nahuat/att/in2dic_flex_vln_iso.att


clean:
	rm nahuat/fst/*.hfst &
	rm nahuat/att/*.att
