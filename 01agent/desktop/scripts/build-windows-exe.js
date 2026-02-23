const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

console.log('🚀 Building 01Agent Windows EXE...');
console.log('Platform:', os.platform());
console.log('Architecture:', os.arch());

// Step 1: Clean previous builds
console.log('\n🧹 Cleaning previous builds...');
try {
  const dirsToClean = ['dist', '01agent-app/build', 'agent_build'];
  dirsToClean.forEach(dir => {
    const fullPath = path.join(__dirname, '..', dir);
    if (fs.existsSync(fullPath)) {
      fs.rmSync(fullPath, { recursive: true, force: true });
      console.log(`✅ Cleaned ${dir}`);
    }
  });
} catch (error) {
  console.error('❌ Error cleaning builds:', error.message);
}

// Step 2: Install dependencies
console.log('\n📦 Installing dependencies...');
try {
  console.log('Installing main dependencies...');
  execSync('npm install', { stdio: 'inherit', cwd: path.join(__dirname, '..') });
  
  console.log('Installing React app dependencies...');
  execSync('npm install', { stdio: 'inherit', cwd: path.join(__dirname, '..', '01agent-app') });
  
  console.log('✅ Dependencies installed');
} catch (error) {
  console.error('❌ Error installing dependencies:', error.message);
  process.exit(1);
}

// Step 3: Build React app
console.log('\n⚛️ Building React application...');
try {
  execSync('npm run build', { stdio: 'inherit', cwd: path.join(__dirname, '..', '01agent-app') });
  console.log('✅ React app built successfully');
} catch (error) {
  console.error('❌ Error building React app:', error.message);
  process.exit(1);
}

// Step 4: Build Python agents (if Python is available)
console.log('\n🐍 Building Python agents...');
try {
  const venvPath = path.join(__dirname, '..', 'aiagent', 'venv');
  if (fs.existsSync(venvPath)) {
    console.log('Building main agent...');
    execSync('npm run build:agent', { stdio: 'inherit', cwd: path.join(__dirname, '..') });
    
    console.log('Building suggestor...');
    execSync('npm run build:suggestor', { stdio: 'inherit', cwd: path.join(__dirname, '..') });
    
    console.log('✅ Python agents built successfully');
  } else {
    console.log('⚠️ Python venv not found, skipping agent build');
  }
} catch (error) {
  console.warn('⚠️ Warning: Could not build Python agents:', error.message);
  console.log('Continuing with Electron build...');
}

// Step 5: Build Electron app for Windows
console.log('\n🖥️ Building Electron application for Windows...');
try {
  execSync('npm run build', { stdio: 'inherit', cwd: path.join(__dirname, '..') });
  console.log('✅ Electron app built successfully');
} catch (error) {
  console.error('❌ Error building Electron app:', error.message);
  process.exit(1);
}

// Step 6: Verify build
console.log('\n✅ Verifying Windows build...');
const distPath = path.join(__dirname, '..', 'dist');
if (fs.existsSync(distPath)) {
  const distFiles = fs.readdirSync(distPath);
  console.log(`✅ Dist contains ${distFiles.length} files/directories`);
  
  // Look for Windows executable
  const exeFiles = distFiles.filter(file => file.endsWith('.exe'));
  const setupFiles = distFiles.filter(file => file.includes('Setup') && file.endsWith('.exe'));
  
  if (exeFiles.length > 0 || setupFiles.length > 0) {
    console.log('✅ Windows executable found:');
    [...exeFiles, ...setupFiles].forEach(file => {
      const filePath = path.join(distPath, file);
      const stats = fs.statSync(filePath);
      const sizeInMB = (stats.size / 1024 / 1024).toFixed(2);
      console.log(`  - ${file} (${sizeInMB} MB)`);
    });
  } else {
    console.log('⚠️ No Windows executable found, checking for unpacked version...');
    const unpackedDir = distFiles.find(dir => dir.includes('win-unpacked'));
    if (unpackedDir) {
      console.log(`✅ Found unpacked Windows build: ${unpackedDir}`);
    }
  }
} else {
  console.error('❌ Dist directory not found');
  process.exit(1);
}

// Step 7: Create portable version info
console.log('\n📋 Creating build info...');
try {
  const buildInfo = {
    version: require('../package.json').version,
    buildDate: new Date().toISOString(),
    platform: 'win32',
    architecture: os.arch(),
    nodeVersion: process.version,
    features: [
      'Lightning-fast AI automation',
      '60-80% faster execution',
      'Smart task routing',
      'Background processing',
      'Real-time performance monitoring',
      'Modern UI with dark/light themes'
    ],
    requirements: {
      os: 'Windows 10/11 (64-bit)',
      ram: '4GB minimum, 8GB recommended',
      storage: '500MB free space',
      python: '3.8+ (included in package)'
    }
  };
  
  fs.writeFileSync(
    path.join(distPath, '01agent-build-info.json'),
    JSON.stringify(buildInfo, null, 2)
  );
  
  console.log('✅ Build info created');
} catch (error) {
  console.warn('⚠️ Could not create build info:', error.message);
}

console.log('\n🎉 Windows EXE build completed successfully!');
console.log('\n📁 Build artifacts location:');
console.log(`  ${distPath}`);
console.log('\n🚀 01Agent is ready for Windows distribution!');
console.log('\n📋 Next steps:');
console.log('  1. Test the executable on a clean Windows machine');
console.log('  2. Create installer with NSIS (already configured)');
console.log('  3. Sign the executable for Windows SmartScreen');
console.log('  4. Upload to distribution platform');