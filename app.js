const sql_query = require('./sql');

const createError = require('http-errors');
const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const logger = require('morgan');

const exphbs = require('express-handlebars')
const bodyParser = require('body-parser')
var session = require('cookie-session')
const passport = require('passport')

const app = express();

// Body Parser Config
app.use(bodyParser.urlencoded({
  extended: false
}));

// Authentication Setup
require('dotenv').config()
require('./auth').init(app)
console.log(process.env.SECRET)
console.log(process.env.DATABASE_URL)
app.use(session({
  secret: process.env.SECRET || "haha",
  resave: true,
  saveUninitialized: true
}))
app.use(passport.initialize())
app.use(passport.session())


// View Engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

// Router Setup
require('./routes').init(app);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
