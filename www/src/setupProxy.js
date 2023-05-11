const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://54.234.201.181:31112/function',
      changeOrigin: true,
      pathRewrite: { '^/api': '' },
    })
  );
};
