"use strict";

import * as header from "./header.js";
import * as platform from "./platform.js";

/*********/
/* model */
/*********/

let model = {
  preventEscape: false,
  loading: false,
  header: header.model,
  platform: platform.model,
};

const initialMsg = {
  type: null,
  data: null,
};

/**********/
/* update */
/**********/

async function update(model, msg, dispatch) {
  switch (msg.type) {
    case "HeaderMsg":
      return {
        ...model,
        header: await header.update(model.header, msg.data, dispatch),
      };
    case "PlatformMsg":
      return {
        ...model,
        platform: await platform.update(model.platform, msg.data, dispatch),
      };
    default:
      return model;
  }
}

function dispathCheckEscape(event, dispatch) {
  if (!model.preventEscape) {
    if (
      event.type == "click" ||
      (event.type == "keydown" && event.key == "Escape")
    ) {
      dispatch({
        type: "HeaderMsg",
        data: { type: "CheckEscape", data: event },
      });
      dispatch({
        type: "PlatformMsg",
        data: { type: "CheckEscape", data: event },
      });
    }
  }
}

/********/
/* view */
/********/

async function view(msg, model, dispatch) {
  switch (msg.type) {
    case "HeaderMsg":
      await header.view(msg.data, model.header, dispatch);
    case "PlatformMsg":
      await platform.view(msg.data, model.platform, dispatch);
  }
  loadingView(model);
}

async function initView(dispatch) {
  await injectSvgSprite();
  header.initView(dispatch);
  platform.initView(dispatch);
  document.body.addEventListener("keydown", (event) =>
    dispathCheckEscape(event, dispatch),
  );
}

async function injectSvgSprite() {
  if (!document.getElementById("svg-sprite")) {
    const resp = await fetch("/static/assets/icons/icons.svg");
    const sprite = await resp.text();
    document.body.insertAdjacentHTML("beforebegin", sprite);
  }
}

function loadingView(model) {
  if (model.loading | model.header.loading | model.platform.loading) {
    document.querySelector("link[rel~='icon']").href =
      "/static/assets/icons/loading.svg";
  } else {
    document.querySelector("link[rel~='icon']").href =
      "/static/assets/icons/favicon.svg";
  }
}

/********/
/* init */
/********/

async function init() {
  const dispatch = async (msg) => {
    setTimeout(async () => {
      model = await update(model, msg, dispatch);
      console.log(msg, model);
      await view(msg, model, dispatch);
    }, 10);
  };

  await initView(dispatch);
  dispatch(initialMsg);
  dispatch(header.initialMsg);
  dispatch(platform.initialMsg);
}

window.addEventListener("load", init);
