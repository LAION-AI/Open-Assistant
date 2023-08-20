'use strict';

module.exports = require('child_process').spawnSync || require('./lib/spawn-sync');
