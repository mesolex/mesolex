import { initfunction } from "./app";

if (window.addEventListener) {
  window.addEventListener("load", initFunction);
} else {
  window.attachEvent("onload", initFunction);
}
