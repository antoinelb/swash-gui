import { create, onKey } from "./utils.js";

/*********/
/* model */
/*********/

export const model = {
  loading: false,
  open: false,
  theme: "dark",
  version: null,
};

export const initialMsg = {
  type: "HeaderMsg",
  data: { type: "GetVersion" },
};

/**********/
/* update */
/**********/

export async function update(model, msg, dispatch) {
  dispatch = createDispatch(dispatch);
  switch (msg.type) {
    case "GetVersion":
      getVersion(dispatch);
      return { ...model, loading: true };
    case "GotVersion":
      return { ...model, loading: false, version: msg.data };
    case "ToggleSettings":
      return { ...model, open: !model.open };
    case "ToggleTheme":
      return { ...model, theme: model.theme == "dark" ? "light" : "dark" };
    default:
      return model;
  }
}

function createDispatch(dispatch) {
  return (msg) => dispatch({ type: "HeaderMsg", data: msg });
}

async function getVersion(dispatch) {
  const resp = await fetch("/version");
  const version = await resp.text();
  dispatch({ type: "GotVersion", data: version });
}

/********/
/* view */
/********/

export async function view(msg, model, dispatch) {
  dispatch = createDispatch(dispatch);
  if (model.open) {
    document.getElementById("settings").classList.add("settings--open");
  } else {
    document.getElementById("settings").classList.remove("settings--open");
  }

  if (model.theme == "dark") {
    document.body.classList.remove("light");
  } else {
    document.body.classList.add("light");
  }

  const version = document.querySelector("#version span:last-child");
  if (version.textContent !== model.version) {
    version.textContent = model.version;
  }
}

export function initView(dispatch) {
  dispatch = createDispatch(dispatch);
  const body = document.body;
  body.appendChild(
    create("header", {}, [
      create("h1", {}, [
        "Plateforme de calcul de temps",
        create("br"),
        "de vidange de réservoirs",
      ]),
      create("div", { id: "settings" }, [
        create(
          "button",
          { title: "Basculer réglages (S)" },
          [
            create("svg", { class: "icon" }, [
              create("use", { href: "#icon-menu" }),
            ]),
          ],
          [
            {
              event: "click",
              fct: async () =>
                await dispatch({
                  type: "ToggleSettings",
                }),
            },
          ],
        ),
        create("div", {}, [
          create(
            "button",
            { id: "theme" },
            [
              create("svg", { id: "theme__moon", class: "icon" }, [
                create("use", { href: "#icon-moon" }),
              ]),
              create("svg", { id: "theme__sun", class: "icon" }, [
                create("use", { href: "#icon-sun" }),
              ]),
              create("span", {}, ["Changer thème"]),
              create("span", { class: "hotkey" }, ["T"]),
            ],
            [
              {
                event: "click",
                fct: async () =>
                  await dispatch({
                    type: "ToggleTheme",
                  }),
              },
            ],
          ),
          create("div", { id: "version" }, [
            create("span", {}, ["Version: "]),
            create("span"),
          ]),
        ]),
      ]),
    ]),
  );
  document.addEventListener("keydown", (event) =>
    onKey(
      "S",
      async () =>
        await dispatch({
          type: "ToggleSettings",
        }),
      event,
    ),
  );
  document.addEventListener("keydown", (event) =>
    onKey(
      "T",
      async () =>
        await dispatch({
          type: "ToggleTheme",
        }),
      event,
    ),
  );
}
