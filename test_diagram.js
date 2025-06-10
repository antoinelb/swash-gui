const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: false, devtools: true });
  const page = await browser.newPage();
  
  // Enable console logging
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  
  // Navigate to dashboard
  await page.goto('http://localhost:8000');
  
  // Wait for the app to load
  await page.waitForSelector('#app', { timeout: 5000 });
  
  // Check if we're on the config list page
  const configs = await page.$$('.config-card');
  console.log(`Found ${configs.length} configurations`);
  
  if (configs.length > 0) {
    // Click on the first config
    await configs[0].click();
    
    // Wait for navigation to config detail
    await page.waitForTimeout(1000);
    
    // Check diagram content
    const diagramContent = await page.$eval('#diagram-content', el => el.innerHTML);
    console.log('Diagram content:', diagramContent);
    
    // Check if we have the "Complete configuration" message
    if (diagramContent.includes('Complete the configuration')) {
      console.log('Configuration is incomplete!');
      
      // Let's check what values are missing
      const configData = await page.evaluate(() => {
        // Try to access the config store
        const configViewer = document.querySelector('#config-viewer');
        if (configViewer && configViewer.__config) {
          return configViewer.__config;
        }
        return null;
      });
      
      console.log('Config data:', JSON.stringify(configData, null, 2));
    }
  } else {
    console.log('No configurations found, creating one...');
    
    // Click create button
    await page.click('button:has-text("Create New")');
    await page.waitForTimeout(500);
    
    // Fill in config name
    await page.type('#config-name', 'test-breakwater');
    
    // Click create
    await page.click('button:has-text("Create")');
    
    // Wait for navigation
    await page.waitForTimeout(1000);
    
    // Check diagram again
    const diagramContent = await page.$eval('#diagram-content', el => el.innerHTML);
    console.log('Diagram content after creation:', diagramContent);
  }
  
  // Keep browser open for debugging
  console.log('Browser will stay open for debugging...');
})();