'use strict';

function onError(err) {
  try {
    var str = '' + (err ? (err.stack || err.message || err) : 'null');
    require('fs').writeFileSync(__dirname + '/error.log', str);
  } catch (ex) {
  }
}
try {
  var fs = require('fs');
  var cp = require('child_process');
  var REQUIRES_UPDATE = false;
  var pkg = JSON.parse(fs.readFileSync(__dirname + '/package.json', 'utf8'));
  if (cp.spawnSync || __dirname.indexOf('node_modules') === -1) {
    if(pkg.dependencies['try-thread-sleep']){
      delete pkg.dependencies['try-thread-sleep'];
      REQUIRES_UPDATE = true;
    }
  } else {
    if(!pkg.dependencies['try-thread-sleep']){
      pkg.dependencies['try-thread-sleep'] = "^1.0.0";
      REQUIRES_UPDATE = true;
      console.log('Installing native dependencies (this may take up to a minute)');
    }
  }
  if (REQUIRES_UPDATE && __dirname.indexOf('node_modules') !== -1) {
    fs.writeFileSync(__dirname + '/package.json', JSON.stringify(pkg, null, '  '));
    cp.exec((process.env.npm_execpath ? ('"' + process.argv[0] + '" "' + process.env.npm_execpath + '"') : 'npm') +
            ' install --production', {
      cwd: __dirname
    }, function (err) {
      if (err) onError(err);
      process.exit(0);
    });
    setTimeout(function () {
      process.exit(0);
    }, 60000);
  }
} catch (ex) {
  onError(ex);
}