import React from "react";
import ReactDOM from "react-dom";

import SearchFormSet from "./components/search-formset";

export const initFunction = () => {
  const {
    formset_config: formsetConfig,
    formset_data: formsetData,
    formset_errors: formsetErrors
  } = JSON.parse(document.getElementById("js-init").text).narratives;

  ReactDOM.render(
    <SearchFormSet
      formsetName="narratives"
      formsetData={formsetData}
      formsetErrors={formsetErrors}
      formsetConfig={formsetConfig}
    />,
    document.querySelector("#narrative-search-form")
  );
};
