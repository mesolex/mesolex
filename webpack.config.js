const path = require('path');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
  devtool: 'eval-source-map',
  module: {
    rules: [
      {
        test: /\.ts(x?)$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'ts-loader',
          },
        ],
      },
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
      },
      {
        test: /\.(css|scss)$/,
        loader: ExtractTextPlugin.extract({
          fallback: 'style-loader',
          use: [
            {
              loader: 'css-loader',
              options: {
                sourceMap: true,
              },
            },
            'postcss-loader',
            {
              loader: 'sass-loader',
              options: {
                sourceMap: true,
              },
            },
          ],
        }),
      },
    ],
  },
  entry: {
    home: path.join(__dirname, 'mesolex/static/js/index.js'),
    search: path.join(__dirname, 'lexicon/static/jsx/search/index.jsx'),
    lexicon_scss: path.join(__dirname, 'lexicon/static/scss/index.scss'),
    narratives: path.join(__dirname, 'narratives/static/jsx/index.jsx'),
    dataSearch: path.join(__dirname, 'mesolex_site/static/mesolex_site/ts/search.tsx'),
  },
  output: {
    path: path.join(__dirname, 'mesolex/static/dist'),
    filename: '[name].bundle.js',
  },
  optimization: {
    splitChunks: {
      cacheGroups: {
        vendors: {
          name: 'vendors',
          chunks: 'initial',
          minChunks: 2,
          minSize: 0,
        },
      },
    },
  },
  resolve: {
    extensions: ['.js', '.jsx', '.scss', '.ts', '.tsx'],
    alias: {
      lexicon: path.resolve(__dirname, 'lexicon/static/jsx/search/'),
      narratives: path.resolve(__dirname, 'narratives/static/jsx/'),
      'query-builder': path.resolve(__dirname, 'query_builder/static/ts/'),
      'plyr-src': path.resolve(__dirname, 'node_modules/plyr/src/'),
    },
  },
  plugins: [
    new ExtractTextPlugin({
      filename: '[name].bundle.css',
    }),
  ],
};
