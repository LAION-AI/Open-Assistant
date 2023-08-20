'use strict';

var path = require('path');
var fs = require('fs');
var tmpdir = require('os').tmpdir || require('os-shim').tmpdir;
var cp = require('child_process');
var sleep;
var JSON = require('./json-buffer');
try {
  sleep = require('try-thread-sleep');
} catch (ex) {
  console.warn('Native thread-sleep not available.');
  console.warn('This will result in much slower performance, but it will still work.');
  console.warn('You should re-install spawn-sync or upgrade to the lastest version of node if possible.');
  console.warn('Check ' + path.resolve(__dirname, '../error.log') + ' for more details');
  sleep = function () {};
}

var temp = path.normalize(path.join(tmpdir(), 'spawn-sync'));

function randomFileName(name) {
  function randomHash(count) {
    if (count === 1)
      return parseInt(16*Math.random(), 10).toString(16);
    else {
      var hash = '';
      for (var i=0; i<count; i++)
        hash += randomHash(1);
      return hash;
    }
  }

  return temp + '_' + name + '_' + String(process.pid) + randomHash(20);
}
function unlink(filename) {
  try {
    fs.unlinkSync(filename);
  } catch (ex) {
    if (ex.code !== 'ENOENT') throw ex;
  }
}
function tryUnlink(filename) {
  // doesn't matter too much if we fail to delete temp files
  try {
    fs.unlinkSync(filename);
  } catch(e) {}
}

function invoke(cmd) {
  // location to keep flag for busy waiting fallback
  var finished = randomFileName("finished");
  unlink(finished);
  if (process.platform === 'win32') {
    cmd = cmd + '& echo "finished" > ' + finished;
  } else {
    cmd = cmd + '; echo "finished" > ' + finished;
  }
  cp.exec(cmd);

  while (!fs.existsSync(finished)) {
    // busy wait
    sleep(200);
  }

  tryUnlink(finished);

  return 0;
}

module.exports = spawnSyncFallback;
function spawnSyncFallback(cmd, commandArgs, options) {
  var args = [];
  for (var i = 0; i < arguments.length; i++) {
    args.push(arguments[i]);
  }

  // node.js script to run the command
  var worker = path.normalize(__dirname + '/worker.js');
  // location to store arguments
  var input = randomFileName('input');
  var output = randomFileName('output');
  unlink(output);

  fs.writeFileSync(input, JSON.stringify(args));
  invoke('"' + process.execPath + '" "' + worker + '" "' + input + '" "' + output + '"');
  var res = JSON.parse(fs.readFileSync(output, 'utf8'));
  tryUnlink(input);tryUnlink(output);
  return res;
}
