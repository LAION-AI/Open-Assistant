var os = require('os')
var osShim

'use strict';

// clone the 'os' module object to avoid mutations and unexpected behavior
module.exports = osShim = clone(os)

//
// apply the missing API
//

if (!os.tmpdir) {
  osShim.tmpdir = tmpdir
}

if (!os.platform) {
  osShim.platform = platform
}

if (!os.arch) {
  osShim.arch = arch
}

if (!os.endianness) {
  osShim.endianness = endianness
}

if (!os.EOL) {
  Object.defineProperty(osShim, 'EOL', {
    get: function () {
      return process.platform === 'win32' ? '\n\r' : '\n'
    }
  })
}

function tmpdir() {
  var isWindows = process.platform === 'win32'
  var env = process.env

  if (isWindows) {
    return env.TEMP ||
           env.TMP ||
           (env.SystemRoot || env.windir) + '\\temp';
  } else {
    return env.TMPDIR ||
           env.TMP ||
           env.TEMP ||
           '/tmp';
  }
}

function platform() {
  return process.platform
}

function arch() {
  return process.arch
}

function endianness() {
  var isEndianness = ((new Uint32Array((new Uint8Array([1,2,3,4])).buffer))[0] === 0x04030201)
  return isEndianness ? 'LE' : 'BE'
}

function clone(object) {
  var prop, cloneObj = {}
  for (prop in object) {
    if (object.hasOwnProperty(prop)) {
      cloneObj[prop] = object[prop]
    }
  }
  return cloneObj
}
