import { create, round } from "./utils.js";

/*********/
/* model */
/*********/

const H = [1, 0.0005];
const R = [0.25, 0.0125];
const L = [0.75, 0.015];
const l = [0.5, 0.015];
const h = [0.5, 0.0005];
const r = [5, 0.208];

export const model = {
  loading: false,
  helpOpen: false,
  inputs: {
    shape: "cylinder",
    height: H[0],
    radius: [R[0]],
    length: L[0],
    width: l[0],
    location: h[0],
    orificeRadius: r[0],
    heightUncertainty: H[1],
    radiusUncertainty: R[1],
    lengthUncertainty: L[1],
    widthUncertainty: l[1],
    locationUncertainty: h[1],
    orificeRadiusUncertainty: r[1],
  },
  output: {
    time: null,
    uncertaity: null,
  },
  errors: {
    height: false,
    radius: false,
    length: false,
    width: false,
    location: false,
    orificeRadius: false,
  },
};

export const initialMsg = {
  type: "PlatformMsg",
  data: { type: "GetTime" },
};

const blue = "oklch(50% 0.2195 260.26)";

/**********/
/* update */
/**********/

export async function update(model, msg, dispatch) {
  dispatch = createDispatch(dispatch);
  switch (msg.type) {
    case "CheckEscape":
      checkEscape(model, msg.data, dispatch);
      return model;
    case "ToggleShape":
      dispatch({ type: "GetTime" });
      return {
        ...model,
        inputs: {
          ...model.inputs,
          shape: model.inputs.shape == "cylinder" ? "rectangle" : "cylinder",
        },
      };
    case "UpdateWater":
      return updateWater(model, msg.data, dispatch);
    case "UpdateHeight":
      return updateHeight(model, msg.data, dispatch);
    case "UpdateRadius":
      return updateRadius(model, msg.data, dispatch);
    case "UpdateLength":
      return updateLength(model, msg.data, dispatch);
    case "UpdateWidth":
      return updateWidth(model, msg.data, dispatch);
    case "UpdateLocation":
      return updateLocation(model, msg.data, dispatch);
    case "UpdateOrificeRadius":
      return updateOrificeRadius(model, msg.data, dispatch);
    case "UpdateWaterUncertainty":
      return updateUncertainty(model, "water", msg.data, dispatch);
    case "UpdateHeightUncertainty":
      return updateUncertainty(model, "height", msg.data, dispatch);
    case "UpdateRadiusUncertainty":
      return updateUncertainty(model, "radius", msg.data, dispatch);
    case "UpdateLengthUncertainty":
      return updateUncertainty(model, "length", msg.data, dispatch);
    case "UpdateWidthUncertainty":
      return updateUncertainty(model, "width", msg.data, dispatch);
    case "UpdateLocationUncertainty":
      return updateUncertainty(model, "location", msg.data, dispatch);
    case "UpdateOrificeRadiusUncertainty":
      return updateUncertainty(model, "orificeRadius", msg.data, dispatch);
    case "ToggleHelp":
      return { ...model, helpOpen: !model.helpOpen };
    case "CloseHelp":
      return { ...model, helpOpen: false };
    case "GetTime":
      getTime(model, dispatch);
      return model;
    case "GotTime":
      return {
        ...model,
        output: { time: msg.data.time, uncertainty: msg.data.delta_time },
      };
    default:
      return model;
  }
}

function createDispatch(dispatch) {
  return (msg) => dispatch({ type: "PlatformMsg", data: msg });
}

function checkEscape(model, event, dispatch) {
  if (!model.preventEscape) {
    if (model.helpOpen) {
      if (
        (event.type == "click" && event.target.id == "click-bg") ||
        (event.type == "keydown" && event.key == "Escape")
      ) {
        dispatch({ type: "CloseHelp" });
        event.stopPropagation();
      }
    }
  }
}

function updateWater(model, val, dispatch) {
  val = parseFloat(val.replace(",", "."));
  if (isNaN(val) || val > model.inputs.height) {
    return { ...model, errors: { ...model.errors, water: true } };
  } else {
    dispatch({ type: "GetTime" });
    return {
      ...model,
      errors: { ...model.errors, water: false },
      inputs: {
        ...model.inputs,
        water: val,
      },
    };
  }
}

function updateHeight(model, val, dispatch) {
  val = parseFloat(val.replace(",", "."));
  if (isNaN(val) || val > 1.5) {
    return { ...model, errors: { ...model.errors, height: true } };
  } else {
    dispatch({ type: "GetTime" });
    return {
      ...model,
      errors: { ...model.errors, height: false },
      inputs: {
        ...model.inputs,
        height: val,
        location: Math.min(model.inputs.location, val),
      },
    };
  }
}

function updateRadius(model, val, dispatch) {
  val = parseFloat(val.replace(",", "."));
  if (isNaN(val) || val < 0.15 || val > 0.5) {
    dispatch({ type: "GetTime" });
    return {
      ...model,
      inputs: { ...model.inputs, radius: val },
      errors: { ...model.errors, radius: true },
    };
  } else {
    dispatch({ type: "GetTime" });
    return {
      ...model,
      errors: { ...model.errors, radius: false },
      inputs: { ...model.inputs, radius: val },
    };
  }
}

function updateLength(model, val, dispatch) {
  val = parseFloat(val.replace(",", "."));
  if (isNaN(val) || val < 0.3 || val > 1) {
    return { ...model, errors: { ...model.errors, length: true } };
  } else {
    dispatch({ type: "GetTime" });
    return {
      ...model,
      errors: { ...model.errors, length: false },
      inputs: { ...model.inputs, length: val },
    };
  }
}

function updateWidth(model, val, dispatch) {
  val = parseFloat(val.replace(",", "."));
  if (isNaN(val) || val < 0.3 || val > 1) {
    return { ...model, errors: { ...model.errors, width: true } };
  } else {
    dispatch({ type: "GetTime" });
    return {
      ...model,
      errors: { ...model.errors, width: false },
      inputs: { ...model.inputs, width: val },
    };
  }
}

function updateOrificeRadius(model, val, dispatch) {
  val = parseFloat(val.replace(",", "."));
  if (isNaN(val) || val < 1 || val > 10) {
    return { ...model, errors: { ...model.errors, orificeRadius: true } };
  } else {
    dispatch({ type: "GetTime" });
    return {
      ...model,
      errors: { ...model.errors, orificeRadius: false },
      inputs: { ...model.inputs, orificeRadius: val },
    };
  }
}

function updateLocation(model, val, dispatch) {
  val = parseFloat(val.replace(",", "."));
  if (isNaN(val) || val > model.inputs.height) {
    return { ...model, errors: { ...model.errors, location: true } };
  } else {
    dispatch({ type: "GetTime" });
    return {
      ...model,
      errors: { ...model.errors, location: false },
      inputs: { ...model.inputs, location: val },
    };
  }
}

function updateUncertainty(model, key, val, dispatch) {
  val = parseFloat(val.replace(",", "."));
  if (isNaN(val)) {
    return model;
  } else {
    dispatch({ type: "GetTime" });
    return {
      ...model,
      inputs: {
        ...model.inputs,
        [`${key}Uncertainty`]: val,
      },
    };
  }
}

async function getTime(model, dispatch) {
  const shapeParams =
    model.inputs.shape == "cylinder"
      ? `radius=${model.inputs.radius}&radius_uncertainty=${model.inputs.radiusUncertainty}`
      : `length=${model.inputs.length}&width=${model.inputs.width}&length_uncertainty=${model.inputs.lengthUncertainty}&width_uncertainty=${model.inputs.widthUncertainty}`;
  const params = `height=${model.inputs.height}&orifice_height=${model.inputs.location}&orifice_radius=${model.inputs.orificeRadius}&height_uncertainty=${model.inputs.heightUncertainty}&orifice_height_uncertainty=${model.inputs.locationUncertainty}&orifice_radius_uncertainty=${model.inputs.orificeRadiusUncertainty}`;

  const resp = await fetch(`/compute?${params}&${shapeParams}`);
  const data = await resp.json();
  dispatch({ type: "GotTime", data: data });
}

/********/
/* view */
/********/

export async function view(msg, model, dispatch) {
  dispatch = createDispatch(dispatch);

  inputsView(model);
  cylinderView(model);
  rectangleView(model);
  outputsView(model);
}

export function initView(dispatch) {
  dispatch = createDispatch(dispatch);
  const body = document.body;
  body.appendChild(
    create("main", {}, [
      createInputsSection(dispatch),
      createShapeSection(dispatch),
      createOutputsSection(),
      create(
        "div",
        { id: "click-bg", hidden: true },
        [],
        [
          {
            event: "click",
            fct: (event) => dispatch({ type: "CheckEscape", data: event }),
          },
        ],
      ),
    ]),
  );
}

function createInputsSection(dispatch) {
  return create("section", { id: "inputs" }, [
    create("h2", {}, [create("h2", {}, ["Paramètres"])]),
    ...createShapeInputRow(dispatch),
    ...createInputRow(
      {
        label: "Hauteur de l'eau dans le réservoir (H)",
        error: "La hauteur doit être entre 0,0 et 1,5.",
        id: "height",
        extraClass: "",
        min: 0,
        max: 1.5,
        initial: H,
        valMsg: "UpdateHeight",
        uncertaintyMsg: "UpdateHeightUncertainty",
      },
      dispatch,
    ),
    ...createInputRow(
      {
        label: "Rayon du réservoir (R)",
        error: "Le rayon doit être entre 0,15 et 0,5.",
        id: "radius",
        extraClass: "cylinder",
        min: 0.15,
        max: 0.5,
        initial: R,
        valMsg: "UpdateRadius",
        uncertaintyMsg: "UpdateRadiusUncertainty",
      },
      dispatch,
    ),
    ...createInputRow(
      {
        label: "Longueur du réservoir (L)",
        error: "La longueur doit être entre 0,3 et 1,0.",
        id: "length",
        extraClass: "rectangle",
        min: 0.3,
        max: 1.0,
        initial: L,
        valMsg: "UpdateLength",
        uncertaintyMsg: "UpdateLengthUncertainty",
      },
      dispatch,
    ),
    ...createInputRow(
      {
        label: "Largeur du réservoir (l)",
        error: "La largeur doit être entre 0,3 et 1,0.",
        id: "width",
        extraClass: "rectangle",
        min: 0.3,
        max: 1.0,
        initial: l,
        valMsg: "UpdateWidth",
        uncertaintyMsg: "UpdateWidthUncertainty",
      },
      dispatch,
    ),
    ...createOrificeInputRow(dispatch),
    ...createInputRow(
      {
        label: "Rayon de l'orifice (r)",
        error: "Le rayon doit être entre 1 et 10.",
        id: "orifice-radius",
        extraClass: "orifice",
        min: 1,
        max: 10,
        initial: r,
        valMsg: "UpdateOrificeRadius",
        uncertaintyMsg: "UpdateOrificeRadiusUncertainty",
      },
      dispatch,
    ),
  ]);
}

function createShapeInputRow(dispatch) {
  return [
    create("label", { for: "shape-input" }, ["Forme"]),
    create("div", { id: "shape-input-container" }, [
      create(
        "input",
        { id: "shape-input", type: "checkbox" },
        [],
        [{ event: "change", fct: () => dispatch({ type: "ToggleShape" }) }],
      ),
      create("span", {}, ["Cylindre"]),
      create("span", {}, ["Prisme rectangulaire"]),
      create("span", { id: "shape-input-container__bg" }),
    ]),
  ];
}

function createOrificeInputRow(dispatch) {
  return [
    create("div", { class: "orifice" }, [
      create("label", { for: "location", class: "orifice" }, [
        "Emplacement de l'orifice (h)",
      ]),
      create("div", {}, [
        create(
          "svg",
          { class: "icon" },
          [create("use", { href: "#icon-help-circle" })],
          [
            {
              event: "click",
              fct: () => {
                dispatch({ type: "ToggleHelp" });
              },
            },
          ],
        ),
        create("span", { id: "orifice-help", hidden: true }, [
          "Un emplacement de 0 mettra l'orifice sur la face inférieure du réservoir et un emplacement plus grand le mettra sur la face latérale avec le centre à la hauteur spécifiée",
          create(
            "svg",
            { class: "icon" },
            [create("use", { href: "#icon-x" })],
            [
              {
                event: "click",
                fct: () => {
                  dispatch({ type: "CloseHelp" });
                },
              },
            ],
          ),
        ]),
      ]),
    ]),
    create(
      "input",
      {
        id: "location",
        class: "val orifice",
        type: "number",
        min: 0,
        max: 1,
        step: 0.1,
        value: h[0],
      },
      [],
      [
        {
          event: "input",
          fct: (event) =>
            dispatch({ type: "UpdateLocation", data: event.target.value }),
        },
      ],
    ),
    create("span", { class: "pm orifice" }, ["±"]),
    create(
      "input",
      {
        id: "location-uncertainty",
        class: "uncertaity orifice",
        type: "number",
        min: 0,
        step: 0.0001,
        value: h[1],
      },
      [],
      [
        {
          event: "input",
          fct: (event) =>
            dispatch({
              type: "UpdateLocationUncertainty",
              data: event.target.value,
            }),
        },
      ],
    ),
    create("span", { class: "unit orifice" }, [
      "m",
      create("span", { class: "error-msg" }, [
        "L'emplacement doit être entre 0,0 et 1,0.",
      ]),
    ]),
  ];
}

function createInputRow(
  { label, error, id, extraClass, min, max, initial, valMsg, uncertaintyMsg },
  dispatch,
) {
  const step = max - min < 0.5 ? 0.05 : max - min < 5 ? 0.1 : 1;

  return [
    create("label", { for: id, class: extraClass }, [label]),
    create(
      "input",
      {
        id: id,
        class: `val ${extraClass}`,
        type: "number",
        min: min,
        max: max,
        step: step,
        value: initial[0],
      },
      [],
      [
        {
          event: "input",
          fct: (event) => dispatch({ type: valMsg, data: event.target.value }),
        },
      ],
    ),
    create("span", { class: `pm ${extraClass}` }, ["±"]),
    create(
      "input",
      {
        id: `${id}-uncertainty`,
        class: `uncertainty ${extraClass}`,
        type: "number",
        min: 0,
        step: id == "orifice-radius" ? 0.01 : 0.0001,
        value: initial[1],
      },
      [],
      [
        {
          event: "input",
          fct: (event) =>
            dispatch({ type: uncertaintyMsg, data: event.target.value }),
        },
      ],
    ),
    create("span", { class: `unit ${extraClass}` }, [
      id == "orifice-radius" ? "mm" : "m",
      create("span", { class: "error-msg" }, [error]),
    ]),
  ];
}

function createShapeSection(dispatch) {
  return create("section", { id: "schema" }, [
    create("h2", {}, ["Schéma"]),
    createCylinderView(),
    createRectangularView(),
  ]);
}

function createCylinderView() {
  return create(
    "svg",
    {
      id: "cylinder",
      class: "cylinder",
      viewBox: "0 0 100 50",
    },
    [
      // bottom
      create("ellipse", { cx: 50, cy: 40, rx: 25, ry: 5 }),
      // water
      create("ellipse", {
        cx: 50,
        cy: 20,
        rx: 25,
        ry: 5,
        stroke: blue,
      }),
      // side
      create("line", { x1: 25, x2: 25, y1: 40, y2: 20 }),
      create("line", { x1: 75, x2: 75, y1: 40, y2: 20 }),
      // orifice
      create("ellipse", { cx: 50, cy: 30, rx: 1, ry: 1 }),
      // H
      create(
        "text",
        {
          x: 24,
          y: 22.5,
          "text-anchor": "end",
          "dominant-baseline": "central",
        },
        ["H = 1.0 m"],
      ),
      // R
      create("line", { x1: 50, x2: 75, y1: 40, y2: 40 }),
      create(
        "text",
        {
          x: 50,
          y: 50,
          "text-anchor": "middle",
          "dominant-baseline": "text-after-edge",
        },
        ["R = 0.5 m"],
      ),
      // r
      create(
        "text",
        {
          x: 50,
          y: 27.5,
          "text-anchor": "middle",
          "dominant-baseline": "text-after-edge",
        },
        ["r = 5 mm"],
      ),
      // h
      create(
        "text",
        {
          x: 80,
          y: 35.0,
          "text-anchor": "start",
          "dominant-baseline": "central",
        },
        ["h = 0.5 m"],
      ),
      create("line", { x1: 78, x2: 78, y1: 40, y2: 30 }),
      create("line", { x1: 77, x2: 79, y1: 40, y2: 40 }),
      create("line", { x1: 77, x2: 79, y1: 30, y2: 30 }),
    ],
  );
}

function createRectangularView() {
  return create(
    "svg",
    {
      id: "rectangle",
      class: "rectangle",
      viewBox: "0 0 125 40",
      hidden: true,
    },
    [
      // front
      create("line", { x1: 30, x2: 45, y1: 40, y2: 40 }),
      create("line", { x1: 30, x2: 30, y1: 20, y2: 40 }),
      create("line", { x1: 45, x2: 45, y1: 20, y2: 40 }),
      // back
      create("line", { x1: 55, x2: 70, y1: 20, y2: 20 }),
      create("line", { x1: 55, x2: 55, y1: 0, y2: 20 }),
      create("line", { x1: 70, x2: 70, y1: 0, y2: 20 }),
      // bottom
      create("line", { x1: 30, x2: 55, y1: 40, y2: 20 }),
      create("line", { x1: 45, x2: 70, y1: 40, y2: 20 }),
      // water
      create("line", { x1: 30, x2: 45, y1: 20, y2: 20, stroke: blue }),
      create("line", { x1: 55, x2: 70, y1: 0, y2: 0, stroke: blue }),
      create("line", { x1: 30, x2: 55, y1: 20, y2: 0, stroke: blue }),
      create("line", { x1: 45, x2: 70, y1: 20, y2: 0, stroke: blue }),
      // orifice
      create("ellipse", { cx: 37.5, cy: 30, rx: 1, ry: 1 }),
      // H
      create(
        "text",
        {
          x: 71,
          y: 10,
          "text-anchor": "start",
          "dominant-baseline": "central",
        },
        ["H = 1.0 m"],
      ),
      // L
      create(
        "text",
        {
          x: 60,
          y: 35,
          "text-anchor": "start",
          "dominant-baseline": "text-after-edge",
        },
        ["L = 0.5 m"],
      ),
      // l
      create(
        "text",
        {
          x: 62.5,
          y: 0,
          "text-anchor": "middle",
          "dominant-baseline": "text-after-edge",
        },
        ["l = 0.5 m"],
      ),
      // h
      create("line", { x1: 28, x2: 28, y1: 30, y2: 40 }),
      create("line", { x1: 27, x2: 29, y1: 30, y2: 30 }),
      create("line", { x1: 27, x2: 29, y1: 40, y2: 40 }),
      create(
        "text",
        {
          x: 26,
          y: 35,
          "text-anchor": "end",
          "dominant-baseline": "central",
        },
        ["h = 1.0 m"],
      ),
      // r
      create(
        "text",
        {
          x: 37.5,
          y: 41,
          "text-anchor": "middle",
          "dominant-baseline": "text-before-edge",
        },
        ["r = 1 mm"],
      ),
    ],
  );
}

function createOutputsSection() {
  return create("section", { id: "outputs" }, [
    create("h2", {}, ["Résultat"]),
    create("div", {}, [
      create("div", {}, [
        create("span", { class: "output-label" }, ["t"]),
        create("span", { class: "output-val" }, []),
        create("span", { class: "output-val" }, []),
        create("span", { class: "output-val" }, []),
      ]),
    ]),
  ]);
}

function inputsView(model) {
  if (model.inputs.shape == "cylinder") {
    document.getElementById("shape-input").checked = false;
    [...document.getElementsByClassName("cylinder")].forEach((node) => {
      node.removeAttribute("hidden");
    });
    [...document.getElementsByClassName("rectangle")].forEach((node) => {
      node.setAttribute("hidden", true);
    });
  } else {
    document.getElementById("shape-input").checked = true;
    [...document.getElementsByClassName("cylinder")].forEach((node) => {
      node.setAttribute("hidden", true);
    });
    [...document.getElementsByClassName("rectangle")].forEach((node) => {
      node.removeAttribute("hidden");
    });
  }

  if (model.helpOpen) {
    document.getElementById("orifice-help").removeAttribute("hidden");
    document.getElementById("click-bg").removeAttribute("hidden");
  } else {
    document.getElementById("orifice-help").setAttribute("hidden", true);
    document.getElementById("click-bg").setAttribute("hidden", true);
  }

  if (document.getElementById("location").value != 0) {
    document.getElementById("location").value = model.inputs.location;
  }

  const handleInputError = (id, error) => {
    const input = document.getElementById(id);
    if (error) {
      input.classList.add("error");
      input.nextSibling.nextSibling.nextSibling
        .querySelector("span")
        .classList.add("error");
    } else {
      input.classList.remove("error");
      input.nextSibling.nextSibling.nextSibling
        .querySelector("span")
        .classList.remove("error");
    }
  };

  handleInputError("height", model.errors.height);
  handleInputError("radius", model.errors.radius);
  handleInputError("length", model.errors.length);
  handleInputError("width", model.errors.width);
  handleInputError("location", model.errors.location);
  handleInputError("orifice-radius", model.errors.orificeRadius);

  const location = document.getElementById("location");
  location.setAttribute("max", model.inputs.height);
  location.nextSibling.nextSibling.nextSibling.querySelector(
    "span",
  ).textContent =
    `L'emplacement doit être entre 0,0 et ${model.inputs.height}.`;
}

function cylinderView(model) {
  const radius = ((model.inputs.radius - 0.15) / (0.5 - 0.15)) * (25 - 10) + 10;
  const height = ((model.inputs.height - 0.3) / (1.5 - 0.3)) * (40 - 10) + 10;
  const orificeRadius = ((model.inputs.orificeRadius - 1) / 10) * 0.5 + 0.5;
  const orificeHeight =
    (model.inputs.location / model.inputs.height) * (height - radius / 5);
  const orificeHoleHeight =
    (model.inputs.location / model.inputs.height) * (height - (2 * radius) / 5);

  const ellipses = document.querySelectorAll("#cylinder ellipse");
  const lines = document.querySelectorAll("#cylinder line");
  const texts = document.querySelectorAll("#cylinder text");

  // bottom
  ellipses[0].setAttribute("rx", radius);
  ellipses[0].setAttribute("ry", radius / 5);

  // water
  ellipses[1].setAttribute("rx", radius);
  ellipses[1].setAttribute("ry", radius / 5);
  ellipses[1].setAttribute("cy", 45 - height);

  // side
  lines[0].setAttribute("x1", 50 - radius);
  lines[0].setAttribute("x2", 50 - radius);
  lines[0].setAttribute("y2", 45 - height);
  lines[1].setAttribute("x1", 50 + radius);
  lines[1].setAttribute("x2", 50 + radius);
  lines[1].setAttribute("y2", 45 - height);

  // orifice
  if (model.inputs.location == 0) {
    ellipses[2].setAttribute("cy", 40);
    ellipses[2].setAttribute("rx", orificeRadius);
    ellipses[2].setAttribute("ry", orificeRadius / 5);
  } else {
    ellipses[2].setAttribute("cy", 45 - radius / 5 - orificeHoleHeight);
    ellipses[2].setAttribute("rx", orificeRadius);
    ellipses[2].setAttribute("ry", orificeRadius);
  }

  // H
  texts[0].setAttribute("x", 50 - radius - 1);
  texts[0].setAttribute("y", 40 - height / 2);
  texts[0].textContent = `H = ${model.inputs.height} m`;

  // R
  lines[2].setAttribute("x2", 50 + radius);
  texts[1].textContent = `R = ${model.inputs.radius} m`;

  // r
  texts[2].setAttribute("y", 39 - orificeHoleHeight);
  texts[2].textContent = `r = ${model.inputs.orificeRadius} mm`;
  if (model.inputs.location == 0) {
    ellipses[2].setAttribute("rx", orificeRadius);
    ellipses[2].setAttribute("ry", orificeRadius / 5);
  } else {
    ellipses[2].setAttribute("rx", orificeRadius);
    ellipses[2].setAttribute("ry", orificeRadius);
  }

  // h
  texts[3].textContent = `h = ${model.inputs.location} m`;
  texts[3].setAttribute("x", 55 + radius);
  texts[3].setAttribute("y", 45 - radius / 5 - orificeHeight / 2);
  if (model.inputs.location == 0) {
    lines[3].setAttribute("hidden", true);
    lines[4].setAttribute("hidden", true);
    lines[5].setAttribute("hidden", true);
  } else {
    lines[3].removeAttribute("hidden");
    lines[4].removeAttribute("hidden");
    lines[5].removeAttribute("hidden");
    lines[3].setAttribute("x1", 50 + radius + 2);
    lines[3].setAttribute("x2", 50 + radius + 2);
    lines[3].setAttribute("y2", 45 - radius / 5 - orificeHeight);
    lines[4].setAttribute("x1", 50 + radius + 1);
    lines[4].setAttribute("x2", 50 + radius + 3);
    lines[5].setAttribute("x1", 50 + radius + 1);
    lines[5].setAttribute("x2", 50 + radius + 3);
    lines[5].setAttribute("y1", Math.min(45 - radius / 5 - orificeHeight), 40);
    lines[5].setAttribute("y2", Math.min(45 - radius / 5 - orificeHeight), 40);
  }

  // lines[3].setAttribute("x1", 50 + radius + 2);
  // lines[3].setAttribute("x2", 50 + radius + 2);
  // lines[4].setAttribute("x1", 50 + radius + 1);
  // lines[4].setAttribute("x2", 50 + radius + 3);
  // lines[5].setAttribute("x1", 50 + radius + 1);
  // lines[5].setAttribute("x2", 50 + radius + 3);
  // texts[2].setAttribute("y", Math.min(45 - radius / 5 - orificeHeight - 2, 36));
  // texts[2].textContent = `r = ${model.inputs.orificeRadius} mm`;
  // texts[3].setAttribute("x", 50 + radius + 3);
  // texts[3].setAttribute(
  //   "y",
  //   Math.min(45 - radius / 5 - orificeHeight / 2 - orificeRadius, 40),
  // );
  // texts[3].textContent = `h = ${model.inputs.location} m`;
}

function rectangleView(model) {
  const totalLength = Math.sqrt(30 ** 2 + 30 ** 2);
  const angle = Math.atan(10 / 25);
  const cos = Math.cos(angle);
  const sin = Math.sin(angle);
  const length =
    ((model.inputs.length - 0.3) / (1 - 0.3)) * (totalLength - 10) + 10;
  const height = ((model.inputs.height - 0.3) / (1.5 - 0.3)) * 40 + 10;
  const width = ((model.inputs.width - 0.3) / (1 - 0.3)) * 20 + 10;

  const orificeRadius = ((model.inputs.orificeRadius - 1) / 10) * 0.5 + 0.5;
  const orificeHeight = (model.inputs.location / model.inputs.height) * height;

  const lines = document.querySelectorAll("#rectangle line");
  const ellipses = document.querySelectorAll("#rectangle ellipse");
  const texts = document.querySelectorAll("#rectangle text");

  // front
  lines[0].setAttribute("x2", 30 + width);
  lines[1].setAttribute("y1", 40 - height);
  lines[2].setAttribute("x1", 30 + width);
  lines[2].setAttribute("x2", 30 + width);
  lines[2].setAttribute("y1", 40 - height);
  // back
  lines[3].setAttribute("x1", 30 + cos * length);
  lines[3].setAttribute("x2", 30 + cos * length + width);
  lines[3].setAttribute("y1", 40 - sin * length);
  lines[3].setAttribute("y2", 40 - sin * length);
  lines[4].setAttribute("x1", 30 + cos * length);
  lines[4].setAttribute("x2", 30 + cos * length);
  lines[4].setAttribute("y2", 40 - sin * length);
  lines[4].setAttribute("y1", 40 - sin * length - height);
  lines[5].setAttribute("x1", 30 + cos * length + width);
  lines[5].setAttribute("x2", 30 + cos * length + width);
  lines[5].setAttribute("y2", 40 - sin * length);
  lines[5].setAttribute("y1", 40 - sin * length - height);
  // bottom
  lines[6].setAttribute("x2", 30 + cos * length);
  lines[6].setAttribute("y2", 40 - sin * length);
  lines[7].setAttribute("x1", 30 + width);
  lines[7].setAttribute("x2", 30 + cos * length + width);
  lines[7].setAttribute("y2", 40 - sin * length);
  // water
  lines[8].setAttribute("x2", 30 + width);
  lines[8].setAttribute("y1", 40 - height);
  lines[8].setAttribute("y2", 40 - height);
  lines[9].setAttribute("x1", 30 + cos * length);
  lines[9].setAttribute("x2", 30 + cos * length + width);
  lines[9].setAttribute("y1", 40 - sin * length - height);
  lines[9].setAttribute("y2", 40 - sin * length - height);
  lines[10].setAttribute("x2", 30 + cos * length);
  lines[10].setAttribute("y1", 40 - height);
  lines[10].setAttribute("y2", 40 - sin * length - height);
  lines[11].setAttribute("x1", 30 + width);
  lines[11].setAttribute("x2", 30 + cos * length + width);
  lines[11].setAttribute("y1", 40 - height);
  lines[11].setAttribute("y2", 40 - sin * length - height);
  // orifice
  if (model.inputs.location == 0) {
    ellipses[0].setAttribute("cx", 30 + (width + cos * length) / 2);
    ellipses[0].setAttribute("cy", 40 - (sin * length) / 2);
    ellipses[0].setAttribute("rx", orificeRadius * Math.tan(angle));
    ellipses[0].setAttribute("ry", orificeRadius);
    ellipses[0].setAttribute(
      "transform",
      `rotate(${(angle / (2 * Math.PI)) * 360 + 45} ${30 + (width + cos * length) / 2} ${40 - (sin * length) / 2})`,
    );
  } else {
    ellipses[0].setAttribute("cx", 30 + width / 2);
    ellipses[0].setAttribute("cy", 40 - orificeHeight);
    ellipses[0].setAttribute("rx", orificeRadius);
    ellipses[0].setAttribute("ry", orificeRadius);
    ellipses[0].removeAttribute("transform");
  }
  // H
  texts[0].setAttribute("x", 31 + cos * length + width);
  texts[0].setAttribute("y", 40 - sin * length - height / 2);
  texts[0].textContent = `H = ${model.inputs.height} m`;
  // L
  texts[1].setAttribute("x", 31 + (cos * length) / 2 + width);
  texts[1].setAttribute("y", 45 - (sin * length) / 2);
  texts[1].textContent = `L = ${model.inputs.length} m`;
  // l
  texts[2].setAttribute("x", 30 + cos * length + width / 2);
  texts[2].setAttribute("y", 38 - sin * length - height);
  texts[2].textContent = `l = ${model.inputs.width} m`;
  // h
  if (model.inputs.location == 0) {
    lines[12].setAttribute("hidden", true);
    lines[13].setAttribute("hidden", true);
    lines[14].setAttribute("hidden", true);
    texts[3].setAttribute("y", 40);
    texts[3].textContent = "h = 0 m";
  } else {
    lines[12].removeAttribute("hidden");
    lines[13].removeAttribute("hidden");
    lines[14].removeAttribute("hidden");
    lines[12].setAttribute("y1", 40 - orificeHeight);
    lines[13].setAttribute("y1", 40 - orificeHeight);
    lines[13].setAttribute("y2", 40 - orificeHeight);
    texts[3].setAttribute("y", 40 - orificeHeight / 2);
    texts[3].textContent = `h = ${model.inputs.location} m`;
  }
  // r
  texts[4].setAttribute("x", 30 + width / 2);
  texts[4].textContent = `r = ${model.inputs.orificeRadius} mm`;
}

function outputsView(model) {
  const div = document.querySelector("#outputs div");
  const spans = div.querySelectorAll(".output-val");
  if (model.output.time !== null && model.output.uncertainty !== null) {
    div.removeAttribute("hidden");
    spans[0].textContent = `= ${model.output.time.toFixed(2)} ± ${model.output.uncertainty.toFixed(2)} s`;
    spans[1].textContent = `= ${(model.output.time / 60).toFixed(2)} ± ${(model.output.uncertainty / 60).toFixed(2)} min`;
    spans[2].textContent = `= ${(model.output.time / 3600).toFixed(2)} ± ${(model.output.uncertainty / 3600).toFixed(2)} h`;
  } else {
    div.setAttribute("hidden", true);
  }
}
