const express = require('express');
const path = require('path');

var history = require('connect-history-api-fallback');

var app = express();

app.use(history({
  index: '/front/index.html',
  verbose: true    
})); 
app.use('/front/', express.static(path.join(__dirname, 'dist')));

app.listen(8080);