// Main application entry point

import { createRouter } from './router.js';
import { createConfigListView } from './views/configList.js';
import { createConfigDetailView } from './views/configDetail.js';
import { createConfigCreateView } from './views/configCreate.js';

// Define routes
const routes = [
  {
    path: '/',
    handler: () => createConfigListView()
  },
  {
    path: '/configs',
    handler: () => createConfigListView()
  },
  {
    path: /^\/config\/(?<name>.+)$/,
    handler: (params) => createConfigDetailView(params.name)
  },
  {
    path: '/create',
    handler: () => createConfigCreateView()
  }
];

// Initialize router
const router = createRouter(routes);

// Start application
document.addEventListener('DOMContentLoaded', () => {
  router.start();
});