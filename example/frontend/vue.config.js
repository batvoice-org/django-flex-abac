module.exports = {
  devServer: {
    proxy: {
      '^/flex_abac': {
        target: 'http://127.0.0.1:8000/',
        //target: 'https://labelit.staging.hosting.call.watch/',
        //changeOrigin: true,
        secure: false,
        logLevel: "debug"
      },

      '^/example': {
        target: 'http://127.0.0.1:8000/',
        //target: 'https://labelit.staging.hosting.call.watch/',
        //changeOrigin: true,
        secure: false,
        logLevel: "debug"
      },
    }
  },

  transpileDependencies: [
    'vuetify'
  ]
}