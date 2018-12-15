const path = require('path');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader'
      },
      {
        test: /\.(css|scss)$/,
        loader: ExtractTextPlugin.extract({
          fallback: 'style-loader',
          use: [
            {
              loader: 'css-loader',
              options: {
                sourceMap: true
              }
            },
            'postcss-loader',
            {
              loader: 'sass-loader',
              options: {
                sourceMap: true
              }
            }
          ]
        })
      }
    ]
  },
  entry: {
    search: path.join(__dirname, 'lexicon/static/jsx/search/index.jsx'),
    narratives: path.join(__dirname, 'narratives/static/jsx/index.jsx'),
    lexicon_scss: path.join(__dirname, 'lexicon/static/scss/index.scss'),
  },
  output: {
    path: path.join(__dirname, 'mesolex/static/dist'),
    filename: '[name].bundle.js'
  },
  resolve: {
    extensions: ['.js', '.jsx'],
    alias: {
      'query-builder': path.resolve(__dirname, 'query_builder/static/jsx/')
    }
  },
  plugins: [
    new ExtractTextPlugin({
      filename: '[name].bundle.css'
    })
  ],
}
