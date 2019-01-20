import { initFunction as lexiconInit } from "lexicon/app";
import { initFunction as narrativesInit } from "narratives/app";

if (window.addEventListener) {
  window.addEventListener("load", lexiconInit);
  window.addEventListener("load", narrativesInit);
} else {
  window.attachEvent("onload", lexiconInit);
  window.attachEvent("onload", narrativesInit);
}
