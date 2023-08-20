var expect = require('expect.js')
var os = require('os')
var osCopy = {}
var osShim

var isWin = process.platform === 'win32'
var tmpVar = isWin ? 'TEMP' : 'TMPDIR'
var tmpDir = process.env[tmpVar]
var isNode10 = (/0\.10\./).test(process.versions.node)

var shimAPI = [ 'tmpdir', 'endianness', 'platform', 'arch', 'EOL' ]

describe('os', function () {

  before(function () {
    if (isNode10) {
      shimAPI.forEach(function (prop) {
        osCopy[prop] = os[prop]
        os[prop] = undefined
      })
    }
  })

  before(function () {
    osShim = require('../lib/os')
  })

  after(function () {
    if (isNode10) {
      // restore members references
      shimAPI.forEach(function (prop) {
        os[prop] = osCopy[prop]
      })
    }
  })

  it('should be an object', function () {
    expect(osShim).to.be.an('object')
  })

  it('should be a clone object', function () {
    expect(osShim).to.not.equal(os)
  })

  describe('API', function () {

    describe('tmpdir()', function () {

      before(function () {
        process.env[tmpVar] = '/custom/tmp'
      })

      after(function () {
        process.env[tmpVar] = tmpDir
      })

      it('should be expose the method', function () {
        expect(osShim.tmpdir).to.be.a('function')
      })

      it('should use the exposed shim method', function () {
        expect(osShim.tmpdir).to.not.be.equal(os.tmpdir)
      })

      it('should have the proper temporary directory path', function () {
        expect(osShim.tmpdir()).to.be.equal('/custom/tmp')
      })

    })

    describe('endianness()', function () {

      it('should be expose the method', function () {
        expect(osShim.endianness).to.be.a('function')
      })

      it('should use the exposed shim method', function () {
        expect(osShim.endianness).to.not.be.equal(os.endianness)
      })

      it('should return the proper endian value', function () {
        expect(osShim.endianness()).to.be.an('string')
        expect(osShim.endianness()).to.match(/LE|BE/)
      })

    })

    describe('EOL', function () {

      it('should be expose the method', function () {
        expect(osShim.EOL).to.be.a('string')
      })

      it('should use the exposed shim method', function () {
        expect(osShim.EOL).to.not.be.equal(os.EOL)
      })

      it('should return the proper EOL value', function () {
        if (isWin) {
          expect(osShim.EOL).to.be.equal('\n\r')
        } else {
          expect(osShim.EOL).to.be.equal('\n')
        }
      })

    })

    describe('platform()', function () {

      it('should be expose the method', function () {
        expect(osShim.platform).to.be.a('function')
      })

      it('should use the exposed shim method', function () {
        expect(osShim.platform).to.not.be.equal(os.platform)
      })

      it('should return the proper EOL value', function () {
        expect(osShim.platform()).to.be.equal(process.platform)
      })

    })

    describe('arch()', function () {

      it('should be expose the method', function () {
        expect(osShim.arch).to.be.a('function')
      })

      it('should use the exposed shim method', function () {
        expect(osShim.arch).to.not.be.equal(os.arch)
      })

      it('should return the proper EOL value', function () {
        expect(osShim.arch()).to.be.equal(process.arch)
      })

    })

  })

})
