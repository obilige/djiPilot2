const express = require('express');
const path = require('path');

var history = require('connect-history-api-fallback');

var app = express();

app.use(history({
  index: '/sample/index.html',
  verbose: true    
})); 
app.use('/sample/', express.static(path.join(__dirname, 'dist')));

app.listen(8081);