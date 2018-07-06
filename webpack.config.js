const path = require('path');

module.exports = {
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        options: {
          presets: [
            ['es2015', {'modules': false}],
            'react',
            'stage-2'
          ]
        }
      }
    ]
  },
  entry: {
    search: path.join(__dirname, 'lexicon/static/jsx/search/index.jsx'),
  },
  output: {
    path: path.join(__dirname, 'mesolex/static/dist'),
    filename: '[name].bundle.js'
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
}
