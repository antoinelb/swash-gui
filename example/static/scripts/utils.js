export function create(type, attributes = {}, children = [], events = []) {
  const node =
    (type == "svg") |
    (type == "use") |
    (type == "ellipse") |
    (type == "line") |
    (type == "text") |
    (type == "rect")
      ? document.createElementNS("http://www.w3.org/2000/svg", type)
      : document.createElement(type);
  Object.keys(attributes).forEach((key) => {
    node.setAttribute(key, attributes[key]);
  });
  children.forEach((child) => {
    if (typeof child === "string") {
      node.appendChild(document.createTextNode(child));
    } else {
      node.appendChild(child);
    }
  });
  events.forEach((event) => {
    node.addEventListener(event.event, event.fct);
  });
  return node;
}

export function onKey(key, callback, event, modifiers) {
  const withCtrl = modifiers ? modifiers.withCtrl | false : false;
  const withAlt = modifiers ? modifiers.withAlt | false : false;
  if (event.target.tagName != "INPUT" && event.target.tagName != "SELECT") {
    if (
      event.key == key &&
      event.ctrlKey == withCtrl &&
      event.altKey == withAlt
    ) {
      callback(event);
      event.preventDefault();
    }
  }
}

export function round(n, d) {
  return Math.round(n * 10 ** d) / 10 ** d;
}
