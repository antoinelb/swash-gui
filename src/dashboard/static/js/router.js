// Simple client-side router using History API

export function createRouter(routes) {
  let currentCleanup = null;
  let currentPath = null;
  
  const navigate = async (path, pushState = true) => {
    // Skip if same path
    if (path === currentPath) return;
    
    // Cleanup previous view
    if (currentCleanup) {
      currentCleanup();
      currentCleanup = null;
    }
    
    // Clear app container
    const app = document.getElementById('app');
    app.innerHTML = '<div class="loading">Loading...</div>';
    
    // Find matching route
    let matchedRoute = null;
    let params = {};
    
    for (const route of routes) {
      if (typeof route.path === 'string' && route.path === path) {
        matchedRoute = route;
        break;
      } else if (route.path instanceof RegExp) {
        const match = path.match(route.path);
        if (match) {
          matchedRoute = route;
          params = match.groups || {};
          break;
        }
      }
    }
    
    if (!matchedRoute) {
      // Default to first route
      matchedRoute = routes[0];
      path = '/';
    }
    
    try {
      // Update URL
      if (pushState) {
        window.history.pushState({}, '', path);
      }
      
      // Create view
      const view = matchedRoute.handler(params);
      currentCleanup = await view.mount();
      currentPath = path;
    } catch (error) {
      console.error('Router error:', error);
      app.innerHTML = `
        <div class="error-message">
          <h2>Error</h2>
          <p>${error.message}</p>
          <button onclick="router.push('/')">Back to Home</button>
        </div>
      `;
    }
  };
  
  const push = (path) => {
    navigate(path, true);
  };
  
  const replace = (path) => {
    window.history.replaceState({}, '', path);
    navigate(path, false);
  };
  
  const start = () => {
    // Handle popstate (back/forward buttons)
    window.addEventListener('popstate', () => {
      navigate(window.location.pathname, false);
    });
    
    // Handle clicks on links
    document.addEventListener('click', (e) => {
      // Check if clicked on a link
      const link = e.target.closest('a[href]');
      if (!link) return;
      
      const href = link.getAttribute('href');
      // Only handle internal links
      if (href && href.startsWith('/') && !href.startsWith('//')) {
        e.preventDefault();
        push(href);
      }
    });
    
    // Navigate to current path
    navigate(window.location.pathname, false);
  };
  
  // Export router instance for global access
  window.router = { push, replace };
  
  return { navigate, push, replace, start };
}