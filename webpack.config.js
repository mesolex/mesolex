const path = require("path");
const ExtractTextPlugin = require("extract-text-webpack-plugin");

module.exports = {
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: "babel-loader"
      },
      {
        test: /\.(css|scss)$/,
        loader: ExtractTextPlugin.extract({
          fallback: "style-loader",
          use: [
            {
              loader: "css-loader",
              options: {
                sourceMap: true
              }
            },
            "postcss-loader",
            {
              loader: "sass-loader",
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
    home: [
      "babel-polyfill",
      path.join(__dirname, "mesolex/static/js/index.js")
    ],
    search: [
      "babel-polyfill",
      path.join(__dirname, "lexicon/static/jsx/search/index.jsx")
    ],
    narratives: [
      "babel-polyfill",
      path.join(__dirname, "narratives/static/jsx/index.jsx")
    ],
    lexicon_scss: path.join(__dirname, "lexicon/static/scss/index.scss")
  },
  output: {
    path: path.join(__dirname, "mesolex/static/dist"),
    filename: "[name].bundle.js"
  },
  optimization: {
    splitChunks: {
      cacheGroups: {
        vendors: {
          name: "vendors",
          chunks: "initial",
          minChunks: 2,
          minSize: 0
        }
      }
    }
  },
  resolve: {
    extensions: [".js", ".jsx"],
    alias: {
      lexicon: path.resolve(__dirname, "lexicon/static/jsx/search/"),
      narratives: path.resolve(__dirname, "narratives/static/jsx/"),
      "query-builder": path.resolve(__dirname, "query_builder/static/jsx/")
    }
  },
  plugins: [
    new ExtractTextPlugin({
      filename: "[name].bundle.css"
    })
  ]
};
