/* eslint import/no-extraneous-dependencies: "off" */

const webpack = require('webpack');

const library = 'webappstuff';

const config = {
  entry: {
    app: './client_modules/js/app.js'
  },
  output: {
    path: __dirname + '/webpack_dist/',
    filename: '[name].bundle.js',
    library: library,
    libraryTarget: 'umd'
  },
  mode: "production",
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader'
        }
      },
    ],
  },
  plugins: [
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
      "window.jQuery": "jquery"
    }),
  ],
  resolve: {
    extensions: ['.js', '.jsx'],
  },
};


module.exports = config;
