const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://gateway/function',
      changeOrigin: true,
      pathRewrite: { '^/api': '' },
    })
  );
};
