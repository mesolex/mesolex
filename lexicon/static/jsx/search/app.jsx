import Plyr from "plyr";

import React from "react";
import ReactDOM from "react-dom";

import SearchFormSet from "./search-formset";

const AUDIO_PLAYER_SELECTOR = "lexical-entry-audio";

export const initFunction = () => {
  const {
    formset_config: formsetConfig,
    formset_data: formsetData,
    formset_global_filters_form_data: formsetGlobalFiltersData,
    formset_errors: formsetErrors
  } = JSON.parse(document.getElementById("js-init").text).lexicon;

  ReactDOM.render(
    <SearchFormSet
      formsetName="lexicon"
      formsetData={formsetData}
      formsetErrors={formsetErrors}
      formsetConfig={formsetConfig}
      formsetGlobalFiltersData={formsetGlobalFiltersData}
    />,
    document.querySelector("#lexicon-search-form")
  );

  Plyr.setup(`.${AUDIO_PLAYER_SELECTOR}`, {
    controls: ['play'],
  });
};