const HtmlWebPackPlugin = require("html-webpack-plugin");
const path = require('path');

const dicotopoAppDevPage = new HtmlWebPackPlugin({
  template: "./src/index.html",
  filename: "./index.html",
  chunks: ["index"]
});

const dicotopoDocsAppDevPage = new HtmlWebPackPlugin({
  template: "./src/docs.html",
  filename: "./docs.html",
  chunks: ["docs"]
});

module.exports = {
  mode: 'development',
  entry: {
    index: './src/index.js',
    docs: './src/docs.js'
  },
  output: {
    path: path.resolve('../static/js'),
    filename: '[name].bundle.js',
    chunkFilename: '[name].bundle.js',
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      },
      {
        test: /\.(png|woff|woff2|eot|ttf|svg)$/,
        loader: 'url-loader?limit=100000'
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"]
      }
    ]
  },
  plugins: [dicotopoAppDevPage, dicotopoDocsAppDevPage],
  node: {
    fs: 'empty'
  }
};